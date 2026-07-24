# Field Guide

A practical reference for working under the expedition framework. The creed (`plugin/creed/`) is the authority on how the roles behave; this guide only shows the trail. Where the two disagree, the creed is right.

## What this is

You are the **patron**: you name a destination worth reaching and why it matters. The agent is the **frontiersman**: it accepts responsibility for finding a way there. The framework gives the two of you a charter to agree on the journey's bounds, ceremonies to keep you seeing the country while the company travels, and a record that lets any future session pick up the journey without you re-explaining it.

Use it for substantial work whose path is not yet known. Do not use it for small, routine, or fully specified tasks — an expedition to the mailbox is overhead, not discipline.

## The shape of a journey

1. **Invoke the expedition skill** in the target project. If a charter under `.expeditions/` already covers the work, the frontiersman resumes it — surveying the camp and briefing you before taking any road the charter leaves open. A company waiting at an agreed basecamp remains there until you send word. Otherwise the frontiersman drafts a charter with you.
2. **Settle the charter together.** The frontiersman counsels first: dangers you have not priced, provisions the work will demand, bounds too tight or too loose, and where review would improve the outcome while correction remains affordable. Push back, adjust, and leave what you cannot settle as riders — questions reserved for you, named in the charter. For each basecamp, agree what work or evidence you will inspect, what judgment is sought, and which consequential choices remain open.
3. **Depart.** After you have seen the draft and the frontiersman's counsel, explicitly accept the charter and send the company out. Language in the initial invocation starts chartering; it does not authorize departure. Departure is the signature, and it opens the journey log at `.expeditions/{name}/journey.jsonl`.
4. **Read the dispatches.** While the company travels you learn through dispatches: miles gained, crossings lost, landmarks found, work to inspect, and the trail ahead. The dispatch orients you to the work; it does not replace seeing it. Expect bad news promptly — a dispatch that only carries good news is a warning sign, not a comfort.
5. **Judge at agreed basecamps.** When the company reaches a basecamp named in the charter, the frontiersman makes the work reviewable, inks the journal, sends a dispatch with counsel, and stops the run. Inspect the work itself. A question keeps the company waiting; your direction puts it back in motion. Your word may open the road beyond, send the company back over the reviewed ground for another crossing, turn it aside onto another route, or return it.
6. **Answer the riders.** When the work hits another question the charter reserved for you — a new horizon, spending beyond provisions, a danger not agreed upon, a purpose out of reach — a rider comes home with the frontiersman's counsel attached. Your answer is logged as your word. Press on, send the company back over known ground, turn aside, or return.
7. **Speak first when you need to.** Any time home learns something the trail cannot, or you want an account or review before the next basecamp, send a missive — invoke the `expedition-missive` skill, or just speak; the ceremony applies either way. A request to pause and inspect makes a basecamp where the company stands. Other missives do not halt the company unless you say so or close a road the charter had left open.
8. **Arrive, or return.** Arrival is judged against the charter's criteria, not against enthusiasm. Either way, the journal holds what was learned before the fire goes out.

## What is expected of you, the patron

- **Name why, not just what.** A destination without a purpose can be reached and still fail its commission. Say what the work should accomplish and what it must never sacrifice.
- **Charter the journey, not every footstep.** Bounds drawn too tight stop the company at every fork to wait for word; bounds too loose make every direction look authorized. Within the charter, a flooded river needs no rider home.
- **Trust the guide enough to be guided.** Ask where the frontiersman would cross, what signs led it there, and what dangers remain unseen — and listen to understand, not to collect reassurance. The final word is always yours.
- **Judge at agreed basecamps.** Reserve judgment where a coherent slice can be inspected while correction remains affordable. Use the dispatch to find the work, then judge its shape, quality, usefulness, and fit. Answer promptly; waiting spends provisions.
- **Answer the riders.** An unanswered rider stalls exactly the decisions you reserved for yourself.
- **Judge the journey, not the route.** A changed route may mean the frontiersman watched the land. Judge whether the expedition kept faith with its purpose, stayed within the charter, spent provisions wisely, and sent honest accounts. Punishing every wrong turn teaches the company to conceal them.
- **Be willing to choose again.** When the land changes the journey's value or its cost, only you can decide whether the destination is still worth reaching.

## Common pitfalls

**Chartering from the study.** Handing down a finished charter and skipping the counsel. The settling is where dangers get priced; a charter the frontiersman merely receives is one it may not be able to keep faith with.

**The everything-charter.** Trying to name every fork in advance. No charter can, and one that tries recreates the step-by-step management the framework exists to replace. Name the bounds and the riders; leave the trail to the frontiersman.

**The unbroken march.** Leaving a substantial expedition with no agreed basecamp invites it to run from departure to arrival before you see the nearer country. Reserve judgment at landmarks where new evidence could change the journey's value, cost, or direction. Do not turn every crossing into a gate.

**Reviewing the dispatch instead of the work.** A polished account can hide an unhelpful result. Follow its references, inspect the actual work or evidence, and give the judgment the camp was built to receive.

**Choosing the trail from home.** Judging the work's shape, quality, usefulness, or character is the patron's responsibility. Prescribing how every correction must be carried out without hearing the frontiersman's counsel chooses the trail. The distinction preserves review without turning it into step-by-step management.

**Treating a missive as a new charter.** Changed terms get counsel on their cost first; then your word stands, and traveling on signs the amendment. Expect the counsel; don't expect the frontiersman to make a hard choice look safe.

**Costume vocabulary.** The metaphor is the interface for the ceremonies, not for the work. If commits, code, or documents start arriving named in expedition vocabulary, that is a fault — the work products belong to the plain language of their craft.

**Skipping the journal.** Ending a session without the journal inked leaves the next session to rediscover the day at full price. The camp is not made until the journal is inked; hold the frontiersman to it.

**A silent log.** The journey log is append-only memory, not paperwork. If sessions end without events, resumption degrades into re-explanation. Nothing obliges any phase to emit any event — but a journey that logged nothing was not being recorded, it was being remembered, and memory is a poor cartographer.

**Punishing the empty-handed scout.** Investigations will return without certainty; crossings will fail. The road home must stay open to unwelcome news, or the news will stop coming.

## Where things live

- `.expeditions/{name}/` in the target project — charter, journey log, dispatches. The persistence mechanism; keep it out of version control if the journey is not the project's business, or track it if you want the record to travel with the repo.
- The journal — dated entries of lessons for the project. Maps, not mandates.
- `plugin/spec/journey-state.md` — the log's format, if you want to read it raw. `plugin/tools/validate` checks a log; `plugin/tools/render` draws it.
