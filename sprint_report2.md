# Sprint 2 Report 
Video Link: 
## What's New (User Facing)
 * Transactions Page: Full transaction display with filtering and search functionality.
 * AI Insights Module: Weekly AI-generated summaries highlighting top spending categories and anomalies.
 * Budgeting Feature: Ability to create, edit, and track category-based budgets with overspending alerts.
 * Authentication & Data Flow Improvements: Fixed session persistence and refresh-token handling for smoother UX.
 

## Work Summary (Developer Facing)
This sprint focused on delivering core financial management features and stabilizing the app’s backend. The team split work based on technical specialization: backend APIs and AI logic (Naven, David), frontend page development and UI refinement (Jayden, Chisomo). The AI Insights feature required integrating FastAPI services with preprocessed transaction data, while the Budgeting module introduced new schemas and endpoints. Team members collaborated through GitHub Issues and Kanban tracking, updating progress daily. We overcame data synchronization issues between the FastAPI backend and the Next.js frontend and refined JWT authentication to prevent session expiration errors.

## Unfinished Work
* Export Reports (PDF/CSV) – Deferred to Sprint 3 for integration with the AI and Transactions modules.
* Dashboard Chart Visualization – Planned but postponed due to time constraints and priority on core functionality.
## Completed Issues/User Stories
Here are links to the issues that we completed in this sprint:

 * https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/issues/11
 * https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/issues/12
 * https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/issues/18

 
 ## Incomplete Issues/User Stories
 Here are links to issues we worked on but did not complete in this sprint:
 
 * URL of issue 1 <<One sentence explanation of why issue was not completed>>
 * URL of issue 2 <<One sentence explanation of why issue was not completed>>
 * URL of issue n <<One sentence explanation of why issue was not completed>>
 
 Examples of explanations (Remove this section when you save the file):
  * "We ran into a complication we did not anticipate (explain briefly)." 
  * "We decided that the feature did not add sufficient value for us to work on it in this sprint (explain briefly)."
  * "We could not reproduce the bug" (explain briefly).
  * "We did not get to this issue because..." (explain briefly)

## Code Files for Review
Please review the following code files, which were actively developed during this sprint, for quality:
 * [backend/app/api/insights.py](https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/blob/main/backend/app/api/insights.py)
 * [backend/app/api/budgets.py](https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/blob/main/backend/app/api/budgets.py)
 * [backend/app/api/transactions.py](https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/blob/main/backend/app/api/transactions.py)
 * [src/app/insights/page.tsx](https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/blob/main/frontend/src/app/insights/page.tsx)
 * [src/app/budgeting/page.tsx](https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/blob/main/frontend/src/app/budgeting/page.tsx)
 * [src/app/transactions/page.tsx](https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/blob/main/frontend/src/app/transactions/page.tsx)

## Retrospective Summary
Here's what went well:
  * Strong collaboration and consistent Kanban updates.
  * Successful integration of backend APIs and frontend pages.

Here's what we'd like to improve:
  * Time management across multiple courses and deliverables.
  * Clearer frontend merge strategy to avoid conflicts.
  * Better estimation of feature scope during planning.
  
Here are changes we plan to implement in the next sprint:
  * Implement Export Reports (PDF/CSV) functionality.
  * Add Financial Goals tracking (US-08).
  * Enhance Dashboard Visuals with charts and analytics widgets.