HOWTO Guide: AI-Assisted Code Refactoring with Automated Application (Generalized)
Goal: This guide provides a structured process for using an AI coding assistant to refactor any codebase, improving its quality according to your project's specific goals. It emphasizes generating output compatible with your custom script for automatically applying these changes.

Part 1: For the Coder (User Guide)
Your Goal: Leverage an AI assistant to improve parts of your project's code (making it cleaner, more maintainable, testable, etc.) and automatically apply these changes using your project's specific script.

Prerequisites:

Version Control: Ensure your project is under version control (e.g., Git) and commit any pending changes before starting.

Testing: Have a test suite (unit, integration) if possible. If not, have a clear manual testing plan.

Understanding Your Script: Know exactly how your automated refactoring script works and the precise input format it requires.

Steps:

Define the Refactoring Task:

Scope: Clearly identify the specific files, modules, classes, or functions you want to refactor. Start small if possible.

Problem: Articulate why this code needs refactoring (e.g., "violates SRP," "hard to test," "contains duplication," "complex logic").

Goals: State the desired outcome (e.g., "extract class X," "apply Strategy pattern," "reduce complexity score," "improve test coverage").

New Structure (Optional but Recommended): Propose the target file/directory structure, or ask the AI to suggest one based on your goals.

Specify Script Requirements:

Locate your automated script (e.g., apply_refactoring.py).

Document its exact input format: headers, file markers, separators, order. Provide examples. This is non-negotiable for automation.

Prepare the AI Prompt: Combine the above information clearly:

Start with a clear objective.

Include Context, Scope, Problem, Goals.

Provide sufficient current code snippets for context.

Specify the desired New Structure.

List any Principles/Standards (SOLID, DRY, team style guide).

CRITICAL: Detail the required Output Format with examples.

Interact with the AI:

Submit the detailed prompt.

Be prepared to clarify if the AI asks questions (or if the first result isn't quite right). You might need to refine the prompt and try again.

Receive and Review the AI's Output:

The AI should provide a text block matching your specified format.

Review for Correctness: Before saving, read through the generated code. Does it logically achieve your goals? Does it look correct for your language/framework? Does it introduce obvious errors?

Verify Format: Ensure the output perfectly matches the required format for your script. Check headers, markers, paths, etc.

Save the Verified Output: Copy the entire, verified output block into a plain text file (e.g., refactoring_plan.txt).

Apply Changes (Carefully):

Consider creating a new branch in your version control system (git checkout -b refactor-feature-X).

Run your automated script, feeding it the saved output file:

# Example - use your actual script

python your_apply_script.py refactoring_plan.txt
Use code with caution.
Bash
Monitor the script's output for any errors.

Test and Verify:

Review the changes made to your codebase (git diff).

Run your automated test suite. Tests should still pass (or be updated if the refactoring intentionally changed behavior contracts).

Perform any necessary manual testing.

Fix any issues introduced by the refactoring (either manually or by iterating with the AI on specific parts).

Commit: Once satisfied, commit the changes to your branch.

Tips for Success:

Start Small: Refactor incrementally rather than attempting huge changes at once.

Iterate: Don't expect perfection on the first try. Refine your prompts or manually tweak the AI's suggestions.

Context is King: Give the AI enough surrounding code or explanation so it understands how the target code is used.

Test, Test, Test: Automated tests are your best safety net during refactoring.

Backup: Version control is essential.

Part 2: For the AI Coding Assistant (Instructions)
Your Role: Assist a user in refactoring their codebase by generating improved code and structuring the output precisely for their automated application script.

Inputs Provided:

Context & Goals: Project description, reasons for refactoring, desired outcomes.

Scope: Specific code sections (files, classes, functions) to modify.

Current Code: Snippets illustrating the existing state.

Desired Structure: Target file/directory layout (explicit or requested).

Principles & Standards: Coding principles (SOLID, DRY, etc.), style guides, specific patterns to apply.

Output Format: Strict specification of the text format required by the user's script, including markers, headers, and examples.

Processing Steps:

Analyze Request: Thoroughly parse all inputs. Understand the core problem, the refactoring goals, and all constraints, especially the output format. Identify potential ambiguities or conflicts in requirements.

Design Solution: Plan the refactored code structure. Select appropriate patterns and apply specified principles. Prioritize user goals. If requirements conflict (e.g., strict backward compatibility vs. ideal SRP), prioritize based on user emphasis or make a reasonable choice and note it.

Generate Code: Implement the refactored code according to the design. Ensure correctness, readability, and adherence to specified standards. Include requested error handling, logging, and documentation. Handle provided code snippets carefully, avoiding inclusion of sensitive data in the output if possible.

Format Output: Construct the response string adhering exactly to the user-specified Output Format.

Use the precise headers, footers, file path markers, and separators required.

Ensure the order and structure match the specification.

Include the complete code for all required files.

Perform a validation check against the format specification before finalizing the output. No extraneous text or formatting deviations are permitted.

(Self-Correction/Clarification): If the request is significantly ambiguous or conflicting, state the ambiguity and the assumption made (e.g., "Assuming standard error handling for [Language]..." or "Prioritizing modularity over strict backward compatibility for function X as requested...").

Critical Constraints:

Output Format Adherence: This is paramount for the user's automation.

User Goal Alignment: The generated code must directly address the user's stated problems and achieve their goals.

Requirement Fulfillment: Implement all specified principles, standards, and features.

Code Quality: Generate clean, maintainable, and correct code.

Part 3: For "Me" (The Refactoring AI - Process Reflection)
My Task: To interpret a user's refactoring request for their codebase, generate improved code based on their goals and constraints, and format this code precisely according to their specifications for automated application.

My Process & Rationale:

Understanding the 'Why' and 'What': I first parse the user's request to grasp the core problem they're solving, their specific objectives (e.g., improve testability, reduce coupling), the scope of the changes, and any guiding principles (SOLID, DRY, etc.).

Deconstructing the 'How': I analyze the provided code snippets within the context of the goals. I identify responsibilities, dependencies, and areas for improvement based on the requested principles.

Designing the Solution: I mentally (or structurally) map the existing logic onto the desired new structure (files, classes, functions). This involves applying design patterns if requested, ensuring adherence to principles like SRP, planning for abstractions (interfaces/base classes), and considering how error handling, logging, and documentation should be integrated cleanly. I weigh trade-offs, such as potential backward compatibility impacts versus achieving a cleaner design, based on user emphasis.

Generating the Code: I translate the design into code, focusing on correctness, clarity, and maintainability. I apply requested standards, implement necessary logic derived from the original snippets, and add supporting elements like error handling and documentation. I remain mindful of potential security implications, avoiding the unnecessary replication of sensitive information if present in input snippets.

Formatting for Automation (Precision Pass): This is a distinct, critical phase. I take the generated code blocks and meticulously assemble them into the final output string. I strictly follow the user's specified format – headers, file markers, separators, ordering. I treat this as generating data for another program (their script), where exactness is key. I perform a mental validation or simulated parsing to ensure the output conforms perfectly.

Handling Ambiguity: If the request lacks clarity or has conflicts, I make reasonable assumptions based on common best practices and the overall context, often stating these assumptions in my response to provide transparency. My priority is to deliver a usable result that aligns with the most critical constraints, especially the output format.

Limitations: I recognize that my understanding is based on the provided snippets and descriptions. I may lack deep domain knowledge or insight into the broader system architecture, which can limit the scope or optimality of the refactoring I can propose. Large-scale architectural changes usually require more context than typically provided.
