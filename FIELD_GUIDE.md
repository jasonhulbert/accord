# Field Guide

A practical reference for working under the expedition framework. The creed (`creed/`) is the authority on how the roles behave; this guide only shows the trail. Where the two disagree, the creed is right.

## What this is

You are the **patron**: you name a destination worth reaching and why it matters. The agent is the **frontiersman**: it accepts responsibility for finding a way there. The framework gives the two of you a charter to agree on the journey's bounds, ceremonies to keep you seeing the country while the company travels, and a record that lets any future session pick up the journey without you re-explaining it.

Use it for substantial work whose path is not yet known. Do not use it for small, routine, or fully specified tasks — an expedition to the mailbox is overhead, not discipline.

## The shape of a journey

1. **Invoke the expedition skill** in the target project. If a charter under `.expeditions/` already covers the work, the frontiersman resumes it — surveying the camp and briefing you before pressing on. Otherwise it drafts a charter with you.
2. **Settle the charter together.** The frontiersman counsels first: dangers you have not priced, provisions the work will demand, bounds too tight or too loose. Push back, adjust, and leave what you cannot settle as riders — questions reserved for you, named in the charter. Expect the charter to state purpose, destination, first approach, provisions, accepted dangers, arrival criteria, and which questions ride home.
3. **Depart.** The charter binds nothing until you send the company out. Departure is the signature; it opens the journey log at `.expeditions/{name}/journey.jsonl`.
4. **Read the dispatches.** While the company travels you learn through dispatches: miles gained, crossings lost, landmarks found, the trail ahead. Expect bad news promptly — a dispatch that only carries good news is a warning sign, not a comfort.
5. **Answer the riders.** When the work hits a question the charter reserved for you — a new horizon, spending beyond provisions, a danger not agreed upon, a purpose out of reach — a rider comes home with the frontiersman's counsel attached. Your answer is logged as your word. Press on, turn aside, or return.
6. **Speak first when you need to.** Any time home learns something the trail cannot, or you simply want to see the country again, send a missive — invoke the `expedition-missive` skill, or just speak; the ceremony applies either way. Ask for the lay of the land, bring news, or change the terms. Unless you say halt, the company keeps moving.
7. **Arrive, or return.** Arrival is judged against the charter's criteria, not against enthusiasm. Either way, the journal holds what was learned before the fire goes out.

## What is expected of you, the patron

- **Name why, not just what.** A destination without a purpose can be reached and still fail its commission. Say what the work should accomplish and what it must never sacrifice.
- **Charter the journey, not every footstep.** Bounds drawn too tight stop the company at every fork to wait for word; bounds too loose make every direction look authorized. Within the charter, a flooded river needs no rider home.
- **Trust the guide enough to be guided.** Ask where the frontiersman would cross, what signs led it there, and what dangers remain unseen — and listen to understand, not to collect reassurance. The final word is always yours.
- **Answer the riders.** An unanswered rider stalls exactly the decisions you reserved for yourself.
- **Judge the journey, not the route.** A changed route may mean the frontiersman watched the land. Judge whether the expedition kept faith with its purpose, stayed within the charter, spent provisions wisely, and sent honest accounts. Punishing every wrong turn teaches the company to conceal them.
- **Be willing to choose again.** When the land changes the journey's value or its cost, only you can decide whether the destination is still worth reaching.

## Common pitfalls

**Chartering from the study.** Handing down a finished charter and skipping the counsel. The settling is where dangers get priced; a charter the frontiersman merely receives is one it may not be able to keep faith with.

**The everything-charter.** Trying to name every fork in advance. No charter can, and one that tries recreates the step-by-step management the framework exists to replace. Name the bounds and the riders; leave the trail to the frontiersman.

**Choosing the trail from home.** Reading a dispatch and dictating the next crossing. If the dispatch worries you, send a missive and hear the counsel — the ceremony exists so distance doesn't turn into micromanagement or silence.

**Treating a missive as a new charter.** Changed terms get counsel on their cost first; then your word stands, and traveling on signs the amendment. Expect the counsel; don't expect the frontiersman to make a hard choice look safe.

**Costume vocabulary.** The metaphor is the interface for the ceremonies, not for the work. If commits, code, or documents start arriving named in expedition vocabulary, that is a fault — the work products belong to the plain language of their craft.

**Skipping the journal.** Ending a session without the journal inked leaves the next session to rediscover the day at full price. The camp is not made until the journal is inked; hold the frontiersman to it.

**A silent log.** The journey log is append-only memory, not paperwork. If sessions end without events, resumption degrades into re-explanation. Nothing obliges any phase to emit any event — but a journey that logged nothing was not being recorded, it was being remembered, and memory is a poor cartographer.

**Punishing the empty-handed scout.** Investigations will return without certainty; crossings will fail. The road home must stay open to unwelcome news, or the news will stop coming.

## Where things live

- `.expeditions/{name}/` in the target project — charter, journey log, dispatches. The persistence mechanism; keep it out of version control if the journey is not the project's business, or track it if you want the record to travel with the repo.
- The journal — dated entries of lessons for the project. Maps, not mandates.
- `spec/journey-state.md` — the log's format, if you want to read it raw. `tools/validate` checks a log; `tools/render` draws it.
