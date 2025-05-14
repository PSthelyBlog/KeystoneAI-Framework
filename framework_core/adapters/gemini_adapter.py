import os
from typing import Dict, List, Optional, Any, Tuple
import google.generativeai as genai
from google.ai import generativelanguage as glm # For schema types

from framework_core.lial_core import (
    LLMAdapterInterface,
    Message,
    ToolRequest,
    LLMResponse # Import the TypedDict
)

class GeminiAdapter(LLMAdapterInterface):
    """
    Adapter for Google's Gemini API.
    
    This adapter implements the LLMAdapterInterface for the Gemini model,
    handling authentication, message formatting, and tool declarations.
    """
    
    PREDEFINED_TOOLS_SCHEMA = [
        genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name="executeBashCommand",
                    description="Execute a bash command on the local system",
                    parameters=glm.Schema(
                        type=glm.Type.OBJECT,
                        properties={
                            "command": glm.Schema(type=glm.Type.STRING, description="The bash command to execute"),
                            "working_directory": glm.Schema(type=glm.Type.STRING, description="The directory in which to execute the command"),
                            "icerc_full_text": glm.Schema(type=glm.Type.STRING, description="Full ICERC protocol text (Intent, Command, Expected, Risk)")
                        },
                        required=["command", "icerc_full_text"]
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="readFile",
                    description="Read the contents of a file from the local filesystem",
                    parameters=glm.Schema(
                        type=glm.Type.OBJECT,
                        properties={
                            "file_path": glm.Schema(type=glm.Type.STRING, description="Absolute path to the file to read"),
                            "icerc_full_text": glm.Schema(type=glm.Type.STRING, description="Full ICERC protocol text (Intent, Command, Expected, Risk)")
                        },
                        required=["file_path", "icerc_full_text"]
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="writeFile",
                    description="Write or overwrite a file on the local filesystem",
                    parameters=glm.Schema(
                        type=glm.Type.OBJECT,
                        properties={
                            "file_path": glm.Schema(type=glm.Type.STRING, description="Absolute path to the file to write"),
                            "content": glm.Schema(type=glm.Type.STRING, description="Content to write to the file"),
                            "icerc_full_text": glm.Schema(type=glm.Type.STRING, description="Full ICERC protocol text (Intent, Command, Expected, Risk)")
                        },
                        required=["file_path", "content", "icerc_full_text"]
                    )
                )
            ]
        )
    ]
    
    def __init__(self, config: Dict[str, Any], dcm_instance: Optional[Any] = None) -> None:
        api_key_env_var = config.get("api_key_env_var", "GEMINI_API_KEY")
        api_key = os.environ.get(api_key_env_var)
        
        if not api_key:
            raise ValueError(f"API key not found in environment variable {api_key_env_var}")
        
        genai.configure(api_key=api_key)
        
        model_name = config.get("model_name", "gemini-2.5-flash-preview-04-17")
        
        self.config = config
        self.dcm_instance = dcm_instance
        self.model_name = model_name
        
        # Prepare system instruction by combining general system prompt and active persona
        # This will be passed to GenerativeModel
        self.base_system_instruction_text = None
        if self.dcm_instance and hasattr(self.dcm_instance, "get_document_content"):
            system_instruction_id = config.get("system_instruction_id")
            if system_instruction_id:
                self.base_system_instruction_text = self.dcm_instance.get_document_content(system_instruction_id)
        
        # Note: Active persona will be added to system_instruction per call in send_message_sequence
        # Initialize model without system_instruction here, will apply it dynamically or use start_chat
        self.generative_model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=self.PREDEFINED_TOOLS_SCHEMA,
            generation_config=config.get("generation_config", {})
            # system_instruction will be handled by start_chat or prepended to messages if needed
        )
    
    def _get_dynamic_system_instruction(self, active_persona_id: Optional[str] = None) -> Optional[str]:
        """Constructs the system instruction dynamically including persona."""
        final_system_instruction_parts = []
        if self.base_system_instruction_text:
            final_system_instruction_parts.append(self.base_system_instruction_text)

        if active_persona_id and self.dcm_instance and hasattr(self.dcm_instance, "get_document_content"):
            persona_doc_id_to_fetch = active_persona_id
            if not active_persona_id.startswith("persona_"):
                persona_doc_id_to_fetch = f"persona_{active_persona_id}"
            
            persona_content = self.dcm_instance.get_document_content(persona_doc_id_to_fetch)
            if persona_content:
                final_system_instruction_parts.append(persona_content)
        
        return "\n\n".join(final_system_instruction_parts) if final_system_instruction_parts else None

    def _convert_messages_to_gemini_format(
        self, 
        messages: List[Message] # This should be List[Message] from lial_core
    ) -> List[glm.Content]: # Return type is specific to google library
        """
        Convert internal Message list (excluding system prompts handled by model config)
        to Gemini's Content list for chat history.
        """
        history: List[glm.Content] = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            # Skip system messages here, as they are handled by the model's system_instruction
            if role == "system":
                continue 
            
            gemini_role = "user" # Default
            if role == "user":
                gemini_role = "user"
            elif role == "assistant":
                gemini_role = "model"
            
            if role == "tool_result":
                # Ensure content for tool response is a dict as expected by Gemini
                tool_response_data = {"content": content}
                try:
                    # If content is already a JSON string representing a dict, parse it
                    if isinstance(content, str) and content.strip().startswith("{") and content.strip().endswith("}"):
                        tool_response_data = json.loads(content)
                except json.JSONDecodeError:
                    # If not a valid JSON dict string, wrap it
                    tool_response_data = {"content": content}

                history.append(
                    glm.Content(
                        parts=[glm.Part(
                            function_response=glm.FunctionResponse(
                                name=msg.get("tool_name", "unknown_tool"),
                                response=tool_response_data
                            )
                        )]
                    )
                )
            else: # user or assistant
                history.append(glm.Content(role=gemini_role, parts=[glm.Part(text=content)]))
        return history
    
    def send_message_sequence(
        self, 
        messages: List[Message], 
        active_persona_id: Optional[str] = None
    ) -> LLMResponse:
        
        # Dynamically construct system instruction including persona
        dynamic_system_instruction = self._get_dynamic_system_instruction(active_persona_id)

        # Convert messages to chat history format, excluding any system messages from the list
        # as system instruction is handled separately by Gemini model/chat.
        chat_history_messages = [msg for msg in messages if msg.get("role") != "system"]
        gemini_chat_history = self._convert_messages_to_gemini_format(chat_history_messages)

        # The last message from the original list is the current user prompt (or tool result leading to it)
        # If gemini_chat_history is empty, it means messages only contained system prompts,
        # or it was an empty list to begin with.
        # The actual new "prompt" to send is the last message if it's a user message.
        # If the history ends with an assistant or tool_result, this call implies we want the LLM to continue.
        
        current_prompt_message = None
        if gemini_chat_history:
            # If the last converted message is a 'user' message, that's our prompt.
            # If it's 'model' or 'tool', then we are asking the model to continue from that state.
            # The Gemini API's `start_chat` with history handles this.
            # The `send_message` will be the *new* content.
            # If the history is already complete up to the last user message, the last message IS the new prompt.
            
            # For simplicity, let's assume the very last message in the *original* `messages` list is the one to "send" now,
            # and the preceding ones are history.
            
            if not messages: # Should not happen if controller sends messages
                return LLMResponse(conversation="No messages to send.", tool_request=None)

            last_original_message = messages[-1]
            history_for_chat_start = self._convert_messages_to_gemini_format(messages[:-1]) # All but the last
            
            # Content to send for the current turn
            content_to_send: Any
            if last_original_message["role"] == "tool_result":
                # If the last message is a tool_result, format it as a FunctionResponse part
                tool_response_data = {"content": last_original_message["content"]}
                try:
                    if isinstance(last_original_message["content"], str) and \
                       last_original_message["content"].strip().startswith("{") and \
                       last_original_message["content"].strip().endswith("}"):
                        tool_response_data = json.loads(last_original_message["content"])
                except json.JSONDecodeError:
                    tool_response_data = {"content": last_original_message["content"]}

                content_to_send = glm.Part(
                    function_response=glm.FunctionResponse(
                        name=last_original_message.get("tool_name", "unknown_tool"),
                        response=tool_response_data
                    )
                )
            elif last_original_message["role"] == "user":
                 content_to_send = last_original_message["content"]
            else: # If last message is assistant or system, what to send? This case should be rare.
                  # Let's assume if it's not user or tool_result, we just ask for continuation.
                  # However, Gemini chat expects user input to continue after model.
                  # If the last message is 'assistant', we should typically wait for user input.
                  # This implies an empty `content_to_send` if we just want the model to "think next" without new user input.
                  # For robust handling, if messages end with 'assistant', perhaps return an empty conv.
                if last_original_message["role"] == "assistant":
                    # print("Warning: Sending messages ending with 'assistant' role to LLM. Expecting LLM to continue or error.") # DEBUG
                    # This might error or produce unexpected results with Gemini's chat.
                    # A better approach might be for the controller to ensure a user prompt follows an assistant message.
                    # For now, let's send an empty user message to prompt continuation (hacky)
                    content_to_send = "" # Or handle this state in the controller
                else: # system message as last (unusual)
                    content_to_send = last_original_message["content"]


        else: # No messages in original list after filtering system prompts
            # This means the `messages` list was empty or only contained system messages.
            # This can happen if `_setup_initial_context` fails and then an empty `messages` list is passed.
            # We need *some* content to send to `chat_session.send_message`.
            # If there's a dynamic_system_instruction, we might use that as a first prompt,
            # or the controller should ensure a valid first user message.
            if dynamic_system_instruction and not messages: # First ever call, only system prompt
                content_to_send = "Hello." # A generic first prompt if messages is empty
                history_for_chat_start = []
            elif messages: # Only system messages were in the original 'messages' list
                content_to_send = messages[0]["content"] # Send the first (and only) system message as user prompt
                history_for_chat_start = []
            else: # Truly empty
                 return LLMResponse(conversation="Error: No messages provided to LLM.", tool_request=None)


        # Re-initialize model with dynamic system instruction for this call if it exists
        # This is one way to handle dynamic system instructions with Gemini.
        # Alternatively, if using `genai.ChatSession`, system_instruction is part of its init.
        current_model_config = {
            "model_name": self.model_name,
            "tools": self.PREDEFINED_TOOLS_SCHEMA,
            "generation_config": self.config.get("generation_config", {})
        }
        if dynamic_system_instruction:
            current_model_config["system_instruction"] = dynamic_system_instruction
        
        current_generative_model = genai.GenerativeModel(**current_model_config)
        chat_session = current_generative_model.start_chat(history=history_for_chat_start)

        try:
            response = chat_session.send_message(content_to_send)
            
            conversation_text = ""
            tool_request_data = None
            
            if hasattr(response, 'candidates') and response.candidates and response.candidates[0].content:
                content_obj = response.candidates[0].content
                
                for part in content_obj.parts:
                    if hasattr(part, 'text') and part.text:
                        conversation_text += part.text
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        params = dict(function_call.args) if hasattr(function_call, "args") else {}
                        icerc_text = params.get("icerc_full_text", "Warning: Missing ICERC protocol text from LLM.")
                        
                        tool_request_data = ToolRequest( # Use TypedDict for creation
                            request_id=f"{function_call.name}-{os.urandom(4).hex()}",
                            tool_name=function_call.name,
                            parameters=params,
                            icerc_full_text=icerc_text
                        )
                        break 
            
            return LLMResponse(conversation=conversation_text, tool_request=tool_request_data)
            
        except Exception as e:
            # self.logger.error(f"Gemini API error: {e}", exc_info=True) # Assuming adapter gets a logger
            return LLMResponse(
                conversation=f"Error communicating with Gemini API: {str(e)}",
                tool_request=None
            )