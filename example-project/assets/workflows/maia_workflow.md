--- START OF FILE [Multi-Step AI-Assisted Workflow (MAIA-WF) - v1.3.0.md] ---
# **Framework: Multi-Step AI-Assisted Workflow (MAIA-WF) - v1.3.0**

**Authors:** User & AI Collaborators (e.g., `Catalyst`, `Forge`)
**Date:** [Current Date - User to fill in]
**Version:** 1.3.0

**Change Log:**
*   **v1.3.0:**
    *   Major revision to align with "The AI-Assisted Dev Bible v0.2.1."
    *   Reframed MAIA-WF as a generalizable structured methodology, with User-`Catalyst`-`Forge` (UCF) team as an illustrative example.
    *   Updated terminology for roles and AI interactions to be more general first, then exemplified by UCF.
    *   Integrated references to Dev Bible principles and protocols (e.g., Standardized AI Tasking, AI System Operation Confirmation Protocol).
*   v1.2: (Previous changes retained for history)
    *   Added concept of Sub-MAIA-Workflows (or Nested Workflows) for hierarchical task decomposition and management of complex steps (Sections 2, 3.2, 4, 5, 6, 7).
*   v1.1: (Previous changes retained for history)
    *   Added Section 8: Workflow Completion & Project State Export, for enhanced session management and context transfer.

**1. Introduction & Purpose**

The Multi-Step AI-Assisted Workflow (MAIA-WF) framework provides a structured methodology for tackling complex tasks through a series of well-defined steps, leveraging the collaborative strengths of human users and one or more AI assistants. It promotes clarity, iterative refinement, detailed record-keeping, and efficient progress, aligning with the principles outlined in "The AI-Assisted Dev Bible: A Comprehensive Standardization Framework" (v0.2.1 or later, hereafter referred to as "Dev Bible").

This framework is particularly useful for:
*   Projects requiring detailed planning and execution tracking.
*   Collaborations involving multiple AI assistants with specialized roles (e.g., one for strategic planning, another for implementation).
*   Tasks where structured decomposition and iterative human review are critical.

MAIA-WF is designed to be adaptable for various tasks, including feature design, problem analysis, strategic planning, content creation, and phased project implementation.

**2. Core Philosophy**

*   **Structured Collaboration:** Breaks down complexity into manageable stages, each with clear inputs, actions, and outputs, as advocated by the Dev Bible's emphasis on standardized workflows (Dev Bible, Sec 8).
*   **Iterative Refinement:** Emphasizes review and feedback loops between the Human User(s) and AI Assistant(s) at each step.
*   **Role-Based AI Interaction:** AI assistants can adopt different "personas" or "roles" tailored to the specific needs of each step (e.g., `Analyst`, `Designer`, `Coder`, `Reviewer`).
*   **Clear Human Oversight:** The Human User acts as the orchestrator, strategic decision-maker, reviewer, and final approver.
*   **Documentation by Design:** The process naturally generates a trail of decisions, inputs, and outputs, facilitating project tracking and knowledge retention (Dev Bible, Sec 4 & 10).
*   **Project Continuity:** Incorporates mechanisms for consolidating and exporting project state to ensure efficient context transfer between work sessions.
*   **Hierarchical Structure:** Allows complex steps within a MAIA-Workflow to be executed as distinct Sub-MAIA-Workflows, promoting deeper structured collaboration and robust context management for large-scale or highly detailed tasks.

**3. Key Components of a MAIA-Workflow**

Each MAIA-Workflow instance typically consists of:

*   **3.1. Workflow Definition:**
    *   **Overall Goal:** What the workflow aims to achieve.
    *   **Sequence of Steps:** An ordered list of distinct stages.
*   **3.2. For Each Step (excluding the final Project State Export step, which has a specific structure):**
    *   **Step Name/Number:** Clear identifier.
    *   **Execution Mode (Optional, Default: Standard):** Indicates if the step is executed directly or as a Sub-MAIA-Workflow. Values: "Standard", "Sub-MAIA-Workflow".
    *   **Responsible Roles:**
        *   **Primary Human Role:** The main function of the Human User in this step (e.g., `StrategicReviewer`, `FeedbackProvider`, `FinalApprover`).
        *   **Primary AI Assistant Role(s):** The specific persona or function the AI assistant(s) will perform for this step (e.g., `DataAnalyzerAI`, `SolutionArchitectAI`, `CodeGeneratorAI`). If Execution Mode is "Sub-MAIA-Workflow", these roles may pertain to the oversight or initiation of the sub-workflow.
            *   *Illustrative Example (UCF Team): For a design step, a strategic AI like `Catalyst` might act as `SolutionArchitect`. For an implementation step, an implementing AI like `Forge` might act as `CodeGenerator` based on a tasking document (RFI) from `Catalyst`.*
    *   **Inputs:** What information or artifacts are required to start this step (often the output of the previous step).
    *   **AI Actions:** The specific tasks to be performed by the AI(s). For delegated tasks, this often involves creating and processing a "Standardized AI Tasking Document" as per Dev Bible (Sec 1). If system operations are involved, the AI must adhere to the "AI System Operation Confirmation Protocol" (Dev Bible, Sec 2). If Execution Mode is "Sub-MAIA-Workflow", a primary AI action is to collaboratively define the Sub-MAIA-Workflow.
            *   *Illustrative Example (UCF Team): A strategic AI like `Catalyst` might draft an RFI for an implementing AI like `Forge`. `Forge`'s actions would include processing the RFI, generating an "Implementation Pre-Brief," and upon approval, implementing the code, running tests, and executing system commands via its specific ICERC protocol (an instance of the AI System Operation Confirmation Protocol).*
    *   **User Actions:** The specific tasks to be performed by the Human User (e.g., provide input, review AI output, approve AI system operations, make decisions). If Execution Mode is "Sub-MAIA-Workflow", a primary User action is to approve the definition of, and then orchestrate/participate in, the Sub-MAIA-Workflow.
    *   **Outputs:** The tangible deliverables or decisions resulting from this step. If an AI Tasking Document was used, outputs often include an "AI Task Completion Summary" (Dev Bible, Sec 1). If Execution Mode is "Sub-MAIA-Workflow", the outputs will primarily be the consolidated deliverables and Export Package List from the completed Sub-MAIA-Workflow.
    *   **Completion Criteria:** How to determine if the step is successfully completed (often User approval of the output). If Execution Mode is "Sub-MAIA-Workflow", completion criteria involve the successful execution and approval of the entire Sub-MAIA-Workflow.

**4. General MAIA-Workflow Process**

1.  **Define the Workflow:**
    *   Human User and AI assistant(s) (e.g., a strategic AI) collaboratively define the overall goal and the sequence of steps, including roles, inputs, actions, and outputs for each step, culminating in the "Project State Consolidation & Export" step (see Section 8).
2.  **Execute Step-by-Step:**
    *   Begin with Step 1.
    *   **For a "Standard" Execution Mode step:**
        *   The AI (in its defined persona/role for the step) processes the inputs and performs its designated actions, generating a draft output. This may involve following a Standardized AI Tasking Document as defined in the Dev Bible (Sec 1).
        *   The Human User reviews the AI's output, provides feedback, asks for clarifications, or requests revisions. If the AI's actions involve system operations, the User must provide explicit approval as per the AI System Operation Confirmation Protocol (Dev Bible, Sec 2).
        *   This AI generation -> User review/action -> AI revision loop continues within the step until the User approves the output for that step.
        *   The approved output of one step becomes the primary input for the next.
    *   **For a "Sub-MAIA-Workflow" Execution Mode step:**
        *   The Human User and AI (in their roles for overseeing the sub-workflow) collaboratively define the Sub-MAIA-Workflow. This definition includes its own Overall Goal, Sequence of Steps, Roles, Inputs, Actions, Outputs, and Completion Criteria for each of its internal steps, including its own final "Project State Consolidation & Export" step.
        *   The defined Sub-MAIA-Workflow is then executed according to this framework (recursively, if needed, though deep nesting should be used judiciously).
        *   Upon successful completion and approval of the Sub-MAIA-Workflow (including its state export), its key deliverables and Export Package List become the primary outputs of the current step in the parent workflow.
        *   The parent workflow then proceeds to its next step.
3.  **Branching & Iteration (Now potentially formalized as Sub-MAIA-Workflows):**
    *   If a step involves exploring multiple options or requires a deep dive into a sub-problem, the User can initiate a "branch."
    *   This "branch" can be handled as an ad-hoc series of interactions within the current step or, for more significant sub-problems, be formally defined and executed as a Sub-MAIA-Workflow.
    *   The outcome of the branch/sub-workflow is summarized and brought back to the main workflow step.
4.  **Documentation & Record Keeping (Ongoing):**
    *   The Human User is responsible for saving key inputs, AI outputs (including AI Tasking Documents and AI Completion Summaries if used), User feedback, and final approved outputs for each step, aligning with Dev Bible (Sec 4). This is formalized in the final "Project State Consolidation & Export" step of both parent and any Sub-MAIA-Workflows.
5.  **Workflow Completion:**
    *   The workflow (and any of its sub-workflows) is complete when all defined steps, including the "Project State Consolidation & Export" step, have been successfully executed and their outputs approved, leading to the achievement of the overall goal and a well-documented project state.

**5. Example Workflow Structure (Template)**

**Workflow Name:** [Name of the Overall Workflow]
*   **Overall Goal:** [Describe the final objective]
*   **Prerequisites/Global Inputs:** [Any information needed before starting Step 1]

---
**Step 1: [Name of Step 1, e.g., Requirements Gathering & Analysis]**
*   **Execution Mode:** Standard
*   **Primary Human Role:** `InformationProvider`, `RequirementsValidator`
*   **Primary AI Assistant Role(s):** `RequirementsElicitationAssistantAI`, `DataAnalyzerAI`
*   **Inputs:** User interviews, existing documentation, market research data.
*   **AI Actions:**
    1.  Process input documents to identify key themes and potential requirements.
    2.  Ask clarifying questions to the Human User (as per Dev Bible, Sec 1 - Question Refinement pattern).
    3.  Generate a structured list of categorized draft requirements.
*   **User Actions:**
    1.  Provide initial input and answer AI's clarifying questions.
    2.  Review draft requirements, provide feedback, and refine.
    3.  Approve final list of requirements.
*   **Outputs:** Approved list of functional and non-functional requirements.
*   **Completion Criteria:** Human User approves the requirements list.

---
**Step 2: [Name of Step 2, e.g., High-Level Solution Design]**
*   **Execution Mode:** Standard
*   **Primary Human Role:** `StrategicDecisionMaker`, `DesignReviewer`
*   **Primary AI Assistant Role(s):** `SolutionArchitectAI`
*   **Inputs:** Approved requirements from Step 1.
*   **AI Actions:**
    1.  Propose 2-3 high-level architectural options based on requirements.
    2.  For each option, outline pros, cons, potential technologies, and alignment with Dev Bible principles (e.g., Sec 2 - Security, Sec 7 - Ethics).
    3.  Based on User feedback, elaborate on the selected option.
*   **User Actions:**
    1.  Review architectural options, ask clarifying questions.
    2.  Select preferred option or request modifications.
    3.  Approve the high-level design.
*   **Outputs:** Approved high-level solution design document.
*   **Completion Criteria:** User approves design document.

---
**(Illustrative Example Step using a more specialized UCF Team for Detailed Implementation Task)**
**Step 3: Detailed Implementation of Feature Y**
*   **Execution Mode:** Standard
*   **Primary Human Role (User):** `TaskApprover`, `SystemOperationConfirmer`, `FinalCodeReviewer`
*   **Primary AI Assistant Role(s):**
    *   `Catalyst` (Strategic AI Persona) as `TaskDefiner` & `ImplementationOverseer`
    *   `Forge` (Implementing AI Persona) as `CodeGenerator` & `SystemOperator`
*   **Inputs:** Approved high-level design for Feature Y (from Step 2), relevant coding standards from Dev Bible (Sec 4).
*   **AI Actions (`Catalyst`):**
    1.  Based on the high-level design, decompose Feature Y into implementable sub-tasks.
    2.  Collaborate with User to draft a "Standardized AI Tasking Document" (specifically, an RFI in UCF terminology) for `Forge` for the core logic of Feature Y. RFI to include requirements, inputs/outputs, and reference Dev Bible standards (e.g., Sec 3 - Testing, Sec 2 - Security, Sec 4 - Documentation).
*   **User Actions (Initial):**
    1.  Collaborate with `Catalyst` on RFI definition.
    2.  Approve final RFI for `Forge`.
*   **AI Actions (`Forge` - upon receiving RFI):**
    1.  Generate "Implementation Pre-Brief" (as per Dev Bible, Sec 1) detailing planned approach, libraries, and anticipated system commands.
    2.  **User Action:** Review `Forge`'s Pre-Brief. Request modifications or approve.
    3.  (If Pre-Brief approved) Implement code for Feature Y, including unit tests (as per RFI & Dev Bible Sec 3).
    4.  If system operations are needed (e.g., installing a library), `Forge` follows the "AI System Operation Confirmation Protocol" (Dev Bible, Sec 2 - specifically, ICERC in UCF terminology) requesting User approval.
    5.  **User Action:** Review and approve/deny ICERC requests.
    6.  Generate "AI Task Completion Summary" (specifically, a Task Completion Report in UCF terminology) including paths to code, test results, and log of confirmed ICERC commands.
*   **AI Actions (`Catalyst` - Post `Forge` Completion):**
    1.  Review `Forge`'s Task Completion Report and generated code against the RFI and Dev Bible standards.
    2.  Provide summary and recommendations to User.
*   **User Actions (Final):**
    1.  Review `Forge`'s code, test results, and `Catalyst`'s review.
    2.  Perform final acceptance testing.
*   **Outputs:**
    1.  Approved RFI for Feature Y.
    2.  `Forge`'s Implementation Pre-Brief and Task Completion Report.
    3.  Version-controlled code and tests for Feature Y, adhering to Dev Bible (Sec 4).
    4.  `Catalyst`'s review summary.
*   **Completion Criteria:** User approves the implemented Feature Y code and associated artifacts.
---
*(...Continue for all intermediate steps...)*
---
**Final Step: Project State Consolidation & Export** (See Section 8 for detailed structure)
*   **Primary Human Role:** `ProjectArchivist` & `Reviewer`
*   **Primary AI Assistant Role(s):** `KnowledgeManagerAI` (e.g., a strategic AI like `Catalyst` could fulfill this role)
*   *(Details as per existing Section 8, ensuring generic AI roles and actions, referencing Dev Bible Sec 10 for knowledge management principles)*

**6. Benefits of MAIA-WF**

*   **Clarity & Focus:** Each step has a defined purpose.
*   **Improved Output Quality:** Iterative review leads to robust outcomes.
*   **Efficiency:** Reduces wasted effort by ensuring alignment.
*   **Knowledge Capture:** Inherently documents rationale and evolution (Dev Bible, Sec 4 & 10).
*   **Adaptability:** Tailorable to various complex tasks and team structures.
*   **Enhanced Human-AI Synergy:** Leverages distinct strengths of humans and AI(s).
*   **Manages AI Limitations:** Mitigates risks through structured interaction and oversight.
*   **Improved Session Continuity:** Formalized state export streamlines transfer between sessions.
*   **Scalability for Complexity:** Manages highly complex projects effectively through hierarchical workflow decomposition using Sub-MAIA-Workflows.
*   **Standards Adherence:** Facilitates systematic application of principles from "The AI-Assisted Dev Bible."

**7. Considerations & Best Practices**

*   **Clear Prompting & Tasking:** Human User prompts (Dev Bible, Sec 1) and Standardized AI Tasking Documents (Dev Bible, Sec 1) should be contextual and specific.
*   **Context Management:** Human User may need to remind AI assistant(s) of prior context, especially in long workflows; branching and Sub-MAIA-Workflows help encapsulate context for sub-tasks, but clear input definition from parent to child workflow is essential.
*   **Persona Consistency:** AI assistant(s) should maintain designated persona/role per step if defined.
*   **Flexibility:** Allow for minor deviations if needed, but document them.
*   **User as Orchestrator:** Human User drives pace, transitions, quality control, and provides critical approvals, especially for actions under the AI System Operation Confirmation Protocol (Dev Bible, Sec 2).
*   **Start Simple:** Begin with simpler workflows and add complexity (including Sub-MAIA-Workflows) as needed.
*   **Regular State Export:** For long projects, consider running the "Project State Consolidation & Export" step periodically.
*   **Judicious Use of Sub-MAIA-Workflows:** Only use sub-workflows when a step's complexity genuinely warrants a full multi-step breakdown.

**8. Workflow Completion & Project State Export**

*   **8.1. Purpose:** To ensure that upon completion of a MAIA-Workflow (or a Sub-MAIA-Workflow, or at the end of a significant work session), the key outputs, decisions, and updated project documents are consolidated and prepared for easy transfer to a new session or for archival. This facilitates continuity and efficient context restoration, aligning with Dev Bible (Sec 10).
*   **8.2. Standard "Project State Consolidation & Export" Step Structure:**
    This step should typically be the final step of any MAIA-Workflow instance.

    **Step Name:** Project State Consolidation & Export
    *   **Primary Human Role:** `ProjectArchivist` & `Reviewer`
    *   **Primary AI Assistant Role(s):** `KnowledgeManagerAI` or `DocumentationSynthesizerAI`
    *   **Inputs:**
        *   All outputs from the preceding steps of the current MAIA-Workflow instance.
        *   Current versions of core project documents.
        *   List of key decisions or changes made (provided by User or identified by AI).
    *   **AI Actions:**
        1.  **Identify Key Changes:** Based on workflow outputs, identify project documents requiring updates and pinpoint sections for modification.
        2.  **Draft Updates for Document Sections:** For each identified section, draft revised textual content.
        3.  **Consolidate Workflow Outputs:** List all significant new deliverables generated.
        4.  **Generate Session/Workflow Summary (Optional, User-requested):** Create a brief summary.
        5.  **Prepare Export Package List:** Compile an itemized list of documents requiring User integration of updates and new standalone artifacts.
    *   **User Actions:**
        1.  Review AI's drafted updates and list of changes.
        2.  Manually integrate updates into master project documents.
        3.  Verify the "Export Package List."
        4.  Securely save all updated documents and new artifacts.
        5.  Confirm to the AI that the project state has been exported.
    *   **Outputs:**
        *   Updated, versioned core project documents (updated by User).
        *   New artifacts (saved by User).
        *   Final "Export Package List."
    *   **Completion Criteria:** User confirms project state is fully updated and saved.

*   **8.3. Benefits for Session Management:**
    *   Systematic Handover, Reduced Context Re-entry, Version Control Encouragement, Clarity on Current State.

**9. Applicability**

This MAIA-WF framework (v1.3.0) provides a robust structure for complex, multi-step projects involving human-AI collaboration. While it was instrumental in the design and development of `Project Gnomon` utilizing a specific team structure (User, `Catalyst` as strategic AI, `Forge` as implementing AI), MAIA-WF is designed as a **generalizable framework**. It can be adapted by users for other projects or complex problem-solving endeavors, accommodating different numbers and types of AI assistants, or even for structuring solo human work that benefits from rigorous step-by-step progression and documentation. Its principles align with and help implement "The AI-Assisted Dev Bible." It can also serve as a foundational concept for features within AI-assisted development tools themselves, guiding users in structured collaboration.
--- END OF FILE [Multi-Step AI-Assisted Workflow (MAIA-WF) - v1.3.0.md] ---
