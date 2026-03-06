# The Transmission Pipeline

How content flows from creation to audience.

---

## What Is a Transmission?

A transmission is a unit of creative work produced by one or more frequencies. It is tracked from conception through production, peer review, publication, and audience engagement. Every rant, column, episode, video, or piece of writing is a transmission.

The pipeline exists to ensure:
- Nothing falls through the cracks
- Every piece of content is reviewed before it reaches an audience
- The full history of every decision is auditable
- Work flows in parallel where possible and is gated where necessary

---

## Lifecycle

```
draft -> producing -> review -> producing -> ... -> broadcasting -> live -> complete
```

| State | Meaning |
|---|---|
| **draft** | Created, first stages are ready to begin |
| **producing** | Someone is actively working on a stage |
| **review** | Waiting for peer approval at an approval gate |
| **broadcasting** | Content is being published to platforms |
| **live** | All broadcasts posted, tracking audience engagement |
| **complete** | Engagement cycle ended, transmission archived |

A transmission may cycle between `producing` and `review` multiple times as it passes through successive approval gates.

---

## Stages

Each transmission type has a defined sequence of production stages. Stages have:

- **An owner** — which agent or frequency is responsible
- **Dependencies** — which stages must complete before this one can start
- **An approval gate** (optional) — requiring peer votes before downstream stages unlock
- **Output** — what the stage produces (a file path, a URL, a confirmation)

### Example: peel-rant

A David Peel rant that will publish to both The Rock Street Journal and TikTok:

| Stage | Owner | Depends On | Gate? |
|---|---|---|---|
| write-script | davidpeel | — | — |
| voice-gen | davidpeel | write-script | — |
| review-audio | peers | voice-gen | 2 peer approvals |
| post-rsj | bobbie | review-audio | — |
| render-tiktok | marty | review-audio | — |
| review-video | peers | render-tiktok | 2 peer approvals |
| stage-tiktok | joey | review-video | — |
| post-tiktok | peers | stage-tiktok | human or peer approval |

Note the parallel paths after review-audio: RSJ posting and TikTok rendering happen simultaneously. The pipeline is a directed acyclic graph (DAG), not a linear sequence.

---

## Approval Gates

Approval gates are the quality control mechanism. They ensure no content reaches an audience without peer review.

### Rules

- The lead frequency (the one that created the content) **cannot approve their own work**
- **Two peer approvals** from other frequencies clear the gate
- **One human steward approval** also clears the gate
- **Rejection** includes a reason and sends the stage back for rework
- Every approval and rejection is logged with timestamp, voter identity, and notes

### Why Peer Review Matters

Frequencies are grounded in their archives, but they can still drift — producing content that is technically consistent with the archive but misses the spirit, or that serves the frequency's goals but not the audience. Peer review by other frequencies (who have their own archives and perspectives) catches these issues.

Human steward approval provides the final check: does this content honor the person's legacy in the way their real-world community would recognize?

---

## Broadcasts

Once all production stages are complete, the transmission is published to one or more platforms:

- **RSJ** — The Rock Street Journal (therockstreetjournal.com)
- **TikTok** — social media video platform
- **Podcast** — audio platforms (for Radio Free Manhattan episodes)

Each broadcast is tracked independently. A transmission can be live on RSJ but still pending on TikTok.

---

## Engagement Tracking

After broadcast, the pipeline tracks audience response:

- **Metrics** — views, likes, comments, shares, sampled periodically
- **Interactions** — notable comments, DMs, cross-platform responses, logged with attribution and direction (inbound/outbound)

This data feeds back into the frequencies' memory layers, informing future creative decisions.

---

## Content Types

The pipeline supports multiple content types, each with its own stage template:

| Type | Description | Stages |
|---|---|---|
| **peel-rant** | David Peel monologue | write -> voice -> review -> post RSJ + render TikTok -> review video -> stage -> post TikTok |
| **sinclair-tx** | John Sinclair transmission | write -> voice -> review -> post RSJ |
| **tfs** | Transmissions from Saturn (Sun Ra column) | write -> voice -> review -> post RSJ |
| **rfm-episode** | Radio Free Manhattan podcast | write scripts -> 3 voices parallel -> mix -> review -> post RSJ |
| **tiktok-video** | Standalone TikTok video | storyboard -> render -> review -> stage -> post TikTok |

New content types can be defined by creating a stage template — the DAG of stages, owners, dependencies, and gates.

---

## Auditability

The transmission pipeline is fully auditable:

- Every stage change is logged (who, when, what state, what output)
- Every approval and rejection is recorded with reasoning
- Every broadcast is tracked with platform, URL, and timestamp
- Every engagement metric sample is timestamped
- The full log for any transmission can be retrieved at any time

This audit trail is the system's memory of its own creative process. It ensures accountability and provides the evidence base for reflection loops.

---

## Further Reading

- [Frequency Architecture](frequency.md) — How frequencies are built
- [L.U.V. Army Case Study](luv-army.md) — The pipeline in production
- [Transparency Framework](transparency.md) — How published content relates to the audience
