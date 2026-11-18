## Interview: Greenleaf Property Management · property manager Priya (TRYOUT BRIEF: small on purpose, ~20 min end to end)

Brief: "tenants email maintenance requests all day. I read every one, decide how urgent it is and
who fixes it. want something that sorts the morning pile for me. emergencies can't wait for me to read them"

### G - Goal
A: 40-60 requests a day, I spend my first 2 hours sorting them. success = the pile is sorted before I sit down
A: must NEVER miss an emergency: gas smell, water pouring, no heat when it's freezing, sparks/burning smell

### U - Users
A: tenants send emails (free text, often messy). I'm the one who reads the sorted list
A: on-call tech Marco gets emergencies by phone right away (I call him, the tool just flags them)
A: me every morning: emergencies first, then today's jobs per vendor, then anything it couldn't sort

### I - Inputs
A: the inbox export (file: requests.csv)

id,unit,received,text
R-201,4B,2026-11-17 06:12,"there's water coming through the ceiling in the bathroom, a lot of it"
R-202,2A,2026-11-17 06:40,"kitchen tap drips all night"
R-203,4B,2026-11-17 06:55,"following up - water still coming from ceiling!!"
R-204,7C,2026-11-17 07:05,"I smell gas near the stove"
R-205,3D,2026-11-17 07:20,"dishwasher wont start"
R-206,,2026-11-17 07:31,"light in hallway flickering"
R-207,5A,2026-11-17 07:45,"can you also repaint my living room? and the heater is dead, its 2 degrees outside"
R-208,1B,2026-11-17 08:02,"hi"

A: vendors (file: vendors.csv)

category,vendor,phone
plumbing,FlowRight Plumbing,555-0142
electrical,Spark & Sons,555-0177
appliance,FixIt Appliances,555-0190
heating,WarmWay HVAC,555-0123

### Happy path
R-202 "kitchen tap drips all night" -> plumbing, routine, FlowRight Plumbing

### D - Danger / handoff
A: emergency words (gas, flooding / water pouring, no heat + freezing, sparks, burning) -> EMERGENCY, top of the list, "call Marco now"
A: if it's not sure what it is -> "Needs Priya" list, never guess a vendor
A: never promise the tenant a time, it only sorts

### E - Edges
A: R-203 is the same leak as R-201 (same unit, same problem, follow-up) -> one job, not two
A: R-206 has no unit -> can't be dispatched, goes to Needs Priya
A: R-207 has two things in one email: repaint is not maintenance (out of scope) but the dead heater at 2 degrees is an emergency
A: R-208 "hi" says nothing -> Needs Priya

### S - Scope
A: IN: sort, urgency, category, vendor, duplicates. OUT: emailing tenants, booking vendors, rent, repaints
A: Priya: "show me 3: the dripping tap, the gas smell, and the 'hi' email"
