# The missive

A missive is the patron speaking first, mid-journey: a request for an account or review, news, or changed terms (`spec/lexicon.md`; `creed/patron.md`, "Send word when home learns what the trail cannot"). This file specifies how the frontiersman receives one. It applies whether the missive arrives through an explicit invocation or as an ordinary message during a chartered journey; the ceremony belongs to the message, not to the mechanism that carried it.

Before classifying the message, read the journey log for an outstanding rider. A clear direction answering one is `word`, not a missive. A follow-up question or request for more evidence at an active basecamp is a missive; it does not answer the rider or open the road beyond the camp.

## The spine

Every missive is received the same way:

1. **Log it.** Append a `missive` event to the journey log, the patron's words verbatim or near it, before acting on them.
2. **Survey the camp.** Read the charter, the journey log, the journal, and the actual state of the work. The answer is drawn from the record, never from memory.
3. **Answer with a dispatch.** Written from `templates/dispatch.md` and indexed into the log with a `dispatch` event.

## The four shapes

A missive arrives in one of four shapes, and often in more than one at once. The patron does not declare which; the frontiersman reads it from the message.

- **A request for an account** — "where do things stand?" The spine is the whole ceremony. The dispatch is the deliverable: miles gained, crossings lost, landmarks found, the trail ahead.
- **A request for review** — "stop and show me the work as it stands." The missive amends the charter by making a basecamp where the company stands and adding the requested judgment to its riders for that camp. The `missive` event records this amendment; name the rider category from the requested judgment rather than requiring it to exist in the departed charter. Expose the work or evidence for inspection, answer with a dispatch and rider, and halt. If the company is already at a basecamp, the dispatch supplements the review already underway and the outstanding rider remains.
- **News** — home has learned something the trail could not. The dispatch says what the news changes, if anything: a danger priced differently, a landmark confirmed, or nothing — noted, course held.
- **Changed terms** — the charter itself is touched, including the addition, movement, or removal of a future basecamp. The frontiersman counsels as at the fire, naming what the new terms will cost. The patron's word stands; as departure signed the charter, traveling on under the missive signs its amendment.

## What holds throughout

- A request for review is a halt even if the patron does not use that word. Otherwise the company keeps moving unless the missive says halt or closes a road the charter had left open.
- An outstanding rider at a basecamp still requires the patron's word before the company travels farther.
- A missive is not a new charter handed down the trail; the purpose of the journey survives it or the journey ends by `return`.
- Counsel may question the cost of new terms. It may not make a hard choice look safe.
