## Interview: Lumen Labs IT · IT lead Sam (TRYOUT BRIEF: small on purpose, ~20 min end to end)

Brief: "people ask for laptops in slack, email, hallway. I keep it all in a spreadsheet and lose track.
want one place where a request goes from asked to approved to handed over, and nobody gets something
they shouldn't"

### G - Goal
A: ~15 requests a week. success = I can see every request and what state it's in, and every approval follows the rules
A: must NEVER hand out a laptop that wasn't approved, and never go over a team's budget

### U - Users
A: I (Sam) enter requests and move them along. managers approve their own team's requests
A: me every morning: what's waiting for a manager, what's ready to hand over, what's blocked and why

### I - Inputs
A: requests export (file: requests.csv)

id,employee,team,model,reason,state
L-301,Ana Ruiz,Design,MacBook Pro 14,new hire,submitted
L-302,Ben Cho,Engineering,ThinkPad X1,replace broken,approved
L-303,Ana Ruiz,Design,MacBook Air,second laptop,submitted
L-304,Dee Park,Sales,MacBook Pro 16,wants faster,submitted
L-305,Eli Moss,Engineering,ThinkPad X1,new hire,approved

A: models and stock (file: stock.csv)

model,price,in_stock
MacBook Air,1100,3
MacBook Pro 14,1900,1
MacBook Pro 16,2600,0
ThinkPad X1,1600,2

A: team budgets left this quarter (file: budgets.csv)

team,budget_left
Design,2500
Engineering,4000
Sales,1500

### Happy path
L-301 Ana Ruiz, Design, MacBook Pro 14, new hire -> manager approves -> in stock -> handed over -> Design budget 2500 -> 600

### D - Danger / handoff
A: only a manager can approve, and only for their own team
A: can't approve if the price is more than the team's budget left -> blocked, "over budget"
A: can't hand over unless it's approved AND in stock. out of stock -> waits as "backordered"

### E - Edges
A: L-303 Ana already has a request open (L-301) -> one open request per person, the second one is blocked
A: L-304 MacBook Pro 16 costs 2600, Sales has 1500 -> over budget
A: L-304 is also out of stock
A: states only go forward: submitted -> approved -> handed over (or blocked / backordered). no skipping

### S - Scope
A: IN: requests, states, approval rules, budget, stock. OUT: buying laptops, shipping, returns, slack integration
A: Sam: "show me 3: Ana's new-hire laptop, Dee's over-budget one, and Ana's second request"
