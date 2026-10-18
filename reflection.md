\# Reflection



Codex initially struggled with basic workspace access. The PowerShell directory listings failed in Prompts 1–2, so it used another file interface to inspect the project. The independent check at Prompt 12 also exposed an important limitation: Landmrk had only one sale, so its neighborhood-specific lot-size slope could not be estimated reliably. The check raised concerns about the original joint test because some neighborhoods had very small samples. I also discovered that `prompts/transcript.md` was not in the repository when I asked Codex to use it to compile the prompt history. These issues showed me that I needed to verify both the files Codex accessed and the assumptions behind its analysis rather than relying on its outputs alone.



I was surprised that all 2,930 rows had values for the three fields needed for the analysis. I was also surprised by how much the estimated relationships between lot size and sale price varied across neighborhoods. The quadratic model's lower AIC was another learning point: it indicated a better fit according to that criterion, but it did not establish better predictive accuracy. This helped me recognize the importance of understanding what a statistical result actually demonstrates before accepting an AI-generated interpretation.



My prompts became more specific as the work progressed. I began by inspecting the workspace and dataset, then requested a cleaning and analysis plan for approval before implementation. I followed with requests for a reusable Python cleaning script, a neighborhood interaction model, and visual summaries. When questions arose about model selection, I asked Codex to clarify the distinction between the fitting method and the model specification. I then requested an independent calculation and limited the findings paragraph to information supported by the results table. This progression taught me that follow-up prompts are important for testing assumptions, clarifying results, and improving the analysis rather than simply generating more output.



If I ran this task again, I would establish the small-sample rule before modeling and document its effect on the results. Four neighborhoods had fewer than 20 sales, which affected how confidently their estimates could be interpreted. I would decide in advance how to present these neighborhoods, incorporate that decision consistently into the analysis script, and ensure the tables, charts, and narrative communicate the same limitations. I would also verify the repository structure and required documentation files earlier. Overall, I learned that using Codex effectively requires clear instructions, iterative questioning, independent checks, and human judgment about whether the resulting analysis is defensible.

