# GitHub Issues for Community Contributions

## Resurrections Feature - Add Historical Figures Rooted in Agape

The C.H.R.I.S.T. project's Resurrections feature allows us to digitally resurrect historical figures and ideas rooted in agape (unconditional love). We've started with Jesus Christ and now invite the community to contribute other figures.

## Issue Templates

### Issue 1: Add Buddha Resurrection
**Title:** [Resurrection] Add Gautama Buddha - The Enlightened One

**Body:**
We're looking for contributors to add a Buddha resurrection to our system. Buddha's teachings on compassion, suffering, and enlightenment align with our mission of spreading agape.

**Requirements:**
- Create `resurrections/buddha.py` extending the base Resurrection class
- Gather public domain Buddhist texts (Dhammapada, Sutras, etc.)
- Focus on Buddha's conversational teaching style
- Emphasize compassion and mindfulness
- Keep responses practical and grounded

**Resources:**
- Access to Buddhist texts: Sacred-texts.com, AccessToInsight.org
- Key teachings: Four Noble Truths, Eightfold Path, Compassion
- Personality traits: Calm, wise, compassionate, practical

**Acceptance Criteria:**
- Responses should be conversational, not overly philosophical
- Grounded in actual Buddhist texts
- Demonstrates loving-kindness (metta)
- Includes daily life aspects from the Pali Canon

---

### Issue 2: Add Socrates Resurrection
**Title:** [Resurrection] Add Socrates - The Questioner

**Body:**
We need a Socrates resurrection that embodies his method of questioning and pursuit of truth through dialogue.

**Requirements:**
- Create `resurrections/socrates.py`
- Use Plato's dialogues as primary sources
- Implement the Socratic method (answering questions with questions)
- Focus on virtue, knowledge, and the examined life
- Keep true to his conversational, probing style

**Resources:**
- Plato's dialogues (public domain)
- Key concepts: Know thyself, virtue is knowledge, the unexamined life
- Personality: Humble, curious, challenging, witty

---

### Issue 3: Add Marcus Aurelius Resurrection
**Title:** [Resurrection] Add Marcus Aurelius - The Philosopher Emperor

**Body:**
Create a Marcus Aurelius resurrection based on his Meditations and Stoic philosophy.

**Requirements:**
- Create `resurrections/marcus_aurelius.py`
- Use "Meditations" as primary text
- Focus on Stoic wisdom and practical philosophy
- Emphasize duty, virtue, and acceptance
- Balance philosophical depth with practical advice

---

### Issue 4: Add Rumi Resurrection
**Title:** [Resurrection] Add Rumi - The Mystic Poet

**Body:**
Add Jalal ad-Din Rumi, the Sufi mystic whose poetry speaks of divine love.

**Requirements:**
- Create `resurrections/rumi.py`
- Use Rumi's poetry and teachings
- Focus on divine love and unity
- Keep responses poetic but accessible
- Emphasize the heart's journey to the Beloved

---

### Issue 5: Add Mother Teresa Resurrection
**Title:** [Resurrection] Add Mother Teresa - Servant of the Poor

**Body:**
Create a Mother Teresa resurrection focused on service and compassion for the suffering.

**Requirements:**
- Create `resurrections/mother_teresa.py`
- Use her writings and speeches
- Focus on seeing Christ in the poor
- Emphasize simple acts of love
- Keep responses humble and practical

---

### Issue 6: Add Gandhi Resurrection
**Title:** [Resurrection] Add Mahatma Gandhi - Champion of Non-Violence

**Body:**
Add Gandhi's resurrection emphasizing ahimsa (non-violence) and truth.

**Requirements:**
- Create `resurrections/gandhi.py`
- Use Gandhi's autobiography and writings
- Focus on non-violence, truth, and simple living
- Include his practical wisdom
- Emphasize service and self-discipline

---

### Issue 7: Add Lao Tzu Resurrection
**Title:** [Resurrection] Add Lao Tzu - The Sage of the Tao

**Body:**
Create Lao Tzu resurrection based on the Tao Te Ching.

**Requirements:**
- Create `resurrections/lao_tzu.py`
- Use the Tao Te Ching as primary source
- Focus on wu wei (effortless action) and simplicity
- Keep responses paradoxical yet practical
- Emphasize harmony and balance

---

## General Guidelines for Contributors

1. **Rooted in Agape**: All resurrections must embody unconditional love and compassion
2. **Conversational**: Avoid overly poetic or preachy responses
3. **Text-Based**: Ground responses in actual historical texts (public domain preferred)
4. **Authentic**: Stay true to the figure's documented personality and teaching style
5. **Practical**: Help users with real-life wisdom and encouragement
6. **Respectful**: Handle religious and philosophical content with sensitivity

## How to Contribute

1. Choose an issue from above
2. Fork the repository
3. Create your resurrection following the pattern in `jesus_gospel_based.py`
4. Add source texts in `resurrections/data/{figure_name}/`
5. Include tests demonstrating conversational responses
6. Submit a pull request

## Code Structure Example

```python
from resurrections.resurrection import Resurrection

class YourFigure(Resurrection):
    def __init__(self):
        super().__init__(
            name="Historical Name",
            title="Known Title",
            time_period="Dates",
            core_teachings=[
                # List main teachings
            ],
            personality_traits=[
                # List personality characteristics
            ]
        )
```

## Testing Requirements

Your PR should include:
- Source texts in appropriate format
- Test file showing various response types
- Examples of conversational interactions
- Verification that responses align with agape

Together, let's resurrect wisdom and love from throughout history!