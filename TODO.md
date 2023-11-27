# Isolation

- run as it's own github user for the sandboxed agent
- script that controls bootstrapper as a separate github user and repo permissions
- bank account balance should be tamper proof. use a proxy for open ai calls so we can intercept usage metrics, and handle bank balance as a service from host computer

# Testing

- Setup unit tests for core modules/tools
- Run unit tests as part of bootstrap setup? Github commit hooks for sandboxed repo?

# Autonomy

- Move human in the loop out a bit more, human sends goals and agents have a tool to contact human for help
- Reintroduce chat room concept and allow collaboration between agents (advisor/verifier + worker)
- Advisor can contact human if it needs help advising the worker, otherwise the worker talks directly to the advisor.
- Human sets high level goals and lets the agents do their job.a