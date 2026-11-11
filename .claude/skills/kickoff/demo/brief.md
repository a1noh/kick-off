## Interview: Spoke & Chain bike repair · owner Dev (TRYOUT BRIEF: small on purpose, ~20 min end to end)

Brief: "customers text us all day asking 'is my bike ready?'. want a chat bot that answers that
and lets them pick a pickup time. anything about prices goes to us"

### G - Goal
A: half our calls are "is it ready". success = customer gets status + picks pickup in 1 min
A: must NEVER tell someone another person's bike status

### U - Users
A: customers on the website chat. handoff -> Dev's queue, he calls back
A: Dev every morning: bikes ready for pickup, pickups booked today, who's in the queue

### I - Inputs
A: customer verifies with ticket number + last name
A: repairs export (file: repairs.csv)

ticket,last_name,bike,status,ready_date
T-100,Nguyen,blue Trek,ready,2026-11-09
T-101,nguyen,red Giant,in progress,2026-11-12
T-102,Okafor,Brompton,ready,2026-11-10
T-103,Okafor,Brompton,ready,2026-11-10

A: pickup slots: 10:00, 13:00, 16:00 every day, max 2 pickups per slot

### Happy path
pt: "is my bike ready? T-100 Nguyen"
bot: "Your blue Trek is ready. Pickup times today: 10:00, 13:00 or 16:00. Which works?"
pt: "1pm"
bot: "Booked: pickup Tue Nov 10 at 1:00 PM. Ticket T-100."

### D - Danger / handoff
A: price / quote / "how much" -> "I've passed this to Dev, he'll call you back today." + queue
A: wrong ticket+name 3x -> queue

### E - Edges
A: T-101 not ready -> say the ready date, no pickup booking
A: T-102/T-103 duplicate row
A: names in different casing
A: assume today = Tue 2026-11-10

### S - Scope
A: IN: status, pickup booking, price handoff, queue. OUT: payments, new repairs, SMS
A: Dev: "show me 3 chats: a ready bike, a not-ready one, and a price question"
