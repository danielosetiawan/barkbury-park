# Pawsley Hollow — Series Bible

## The pitch
**"Hammi's Day"** — cozy, wordless slice-of-life videos about a corgi living an
ordinary life in a small town where every resident is an animal. There are no
humans and no dialogue. Each episode has ambient sound, lofi music, and short
on-screen captions ("7:02am — breakfast").

Why this format works for a faceless channel on limited hardware:
- **Slow, calm motion** is what video models do best. Washing dishes, pouring
  tea, and walking to the bus all look good; fight scenes and fast cuts don't.
- **No lip-sync or dialogue**, so nothing has to match speech.
- **Short 3–5s shots that are cut together** look like the style is meant to be
  that way, not like a limit of the tools.
- It works both as **Shorts** (one 15–30s moment) and as **long-form** videos
  (3–8 min "a day in the life" or "relaxing evening routine").

## Visual style lock
Paste this into EVERY prompt, word for word. Keeping it identical is how you
keep the look consistent from shot to shot.

> stylized 3D animated film, cozy storybook town, soft warm lighting, gentle
> depth of field, rounded shapes, rich textures, pastel and warm autumn color
> palette, cinematic composition

Negative prompt (also fixed):

> humans, people, person, human hands, human face, text, watermark, logo, blurry,
> distorted anatomy, extra limbs, extra legs, six legs, extra arms, four legs, on all fours,
> quadruped, deformed paws, flicker, low quality

## Main character — Hammi
- Pembroke Welsh corgi, **red-headed tri-color**, based on the real Hammi:
  rich copper-red head and big ears (pale cream insides), a white blaze up the
  middle of the face to the forehead, white muzzle and chest, a **black saddle**
  across the back, copper-red legs and hips, white paws, soulful dark eyes, short legs, **no tail** (docked, like many Pembrokes; it's in his description because the model added one in ep01 s13).
- **Always upright on two hind legs**, using his front paws as hands (like a cartoon
  character). Never on all fours: mixing the two made the model draw six-legged
  Hammis (arms *and* four legs) in ep01's first render.
- **Wardrobe = identity.** Always: a **mustard-yellow knit sweater** and a **small
  forest-green scarf**. (Dropped: work glasses. The model kept giving them to other characters.)
  Out of the house he wears a **small black school backpack** (both straps on), never a satchel or briefcase.
- Markings: mostly copper-red with just a small patch of black on the hips; never a black rump.
- Personality: earnest, a bit clumsy, finds joy in small rituals.
- **Quirks** (use as running gags and easter eggs, not every episode):
  - **Hates pigeons.** The rooftop pigeons are his nemeses. Gag: Hammi spots
    them watching and hurries to lock the door, narrows his eyes at them, or
    shoos them off his fence. (Ep01 s11 already has the pigeons watching him lock
    up, so it plays as a quiet first hint.)
  - **Loves food.** Lights up at toast, snacks, bakery smells, picnics. Easy
    beats: sniffing the air outside the bakery, staring at a dropped crumb,
    eating the most at every party.
  - **Loves everybody, except cats.** Warm to the whole town but secretly
    suspicious of cats, especially Dany, who is unfailingly nice to
    him. Gag: side-eye from behind a door, refusing her pastry and then caving
    because he loves food (quirk #2 beats quirk #3). Possible arc: he slowly
    warms to her. Continuity note: ep01 (him waving at her) and ep02 (her
    coming to cheer him up) were written before this quirk. Leave them as they
    are; the suspicion can start in a later episode.
- Home: a small cottage with a round blue door, a cluttered warm kitchen,
  hanging plants, a window over the sink.

**Character token** (paste into every Hammi prompt):
> Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (rich copper-red head and big ears with pale cream insides, a white blaze up the middle of the face, white muzzle and chest, a black saddle across the back, copper-red legs, white paws), soulful dark eyes
> and big upright ears, wearing a mustard-yellow knit sweater and a small
> forest-green scarf

## Writing shot prompts
- **Refer to cast members by name only** in a shot's scene text ("Professor Hoot behind the desk"). Their look
  comes from the cast list. Describing them again ("an owl with spectacles…") made the model draw two of them
  (two Pips and two Hoots in ep01's first render).
- **At most one character of each species per shot.** Even "only one owl" makes it draw more owls. Give
  a second same-species character (or a lone supporting character) its own close-up shot instead.
- One action per 4-second shot; split "does X, then Y" into two shots.

## Recurring cast
| Name | Species | Role | Look token |
|---|---|---|---|
| **Bobo** | white bichon poo | **Hammi's best friend and next-door neighbor** | small fluffy white bichon poo with a curly cloud-like coat, round black button eyes and nose, wearing a sky-blue bandana |
| **Dany** (she; "Mrs. Marmalade") | ginger tabby cat | runs the bakery on Hammi's street; Hammi's friend, though he never fully trusts her because she's a cat | plump ginger tabby cat in a flour-dusted pink apron |
| Dwight | river otter | drives the town bus | sleek brown otter in a navy bus-driver cap and vest (small name badge "Dwight" on the left side of the vest); left-handed |
| Professor Hoot | great horned owl | Hammi's teacher at the schoolhouse | stern owl with half-moon spectacles and a tweed waistcoat |
| Toozi | horse | festival and party animal, never misses a show at the park bandstand | tall chestnut horse with a flowing blonde mane, a faded band t-shirt, colorful festival wristbands on one foreleg, headphones around the neck |
| Vivi | dachshund | picky eater, yappy, milk-tea devotee | small solid chocolate-brown smooth-coated dachshund, no collar, long body, floppy ears, always holding a boba milk tea |
| Jul | goat | the most fashionable animal in town, always dressed super hip | slender white goat, curled horns, cropped lavender puffer jacket, bucket hat, round tinted sunglasses, chunky white sneakers |
| Molly | duck | the most excitable animal in town; ecstatic about everything | small round fluffy yellow duck, orange bill and webbed feet, tiny pink polka-dot bow, big sparkly eyes |
| Damian | barn owl | hospital doctor on night shifts who still loves to party | barn owl with a heart-shaped white face and sleepy eyes, teal scrubs, stethoscope |
| Pip | hamster | Hammi's classmate, chaotic energy | tiny golden hamster in an oversized red hoodie |
| Juniper | fox | florist across the street | slender red fox in a green gardening apron |
| The Movers | beavers | two-beaver moving company (ep02) | two cheerful beaver movers in orange overalls |
| The Pigeons | pigeons | Greek chorus, always on the rooftops | three pigeons in little flat caps |

### Bobo
Hammi's best friend, who lives in the cottage next door (yellow door, a white picket
fence between the two gardens). Bobo is the cheerful one: always waving over the
fence, turning up with snacks, dragging Hammi to the park on weekends. The
**sky-blue bandana** is Bobo's identity piece, the way the sweater and scarf are
Hammi's. Good for: morning hellos over the fence, weekend episodes, sharing a
bench at the duck pond, and the "small problem → small win" beat (Bobo is often
the one who helps).

### Toozi (the party horse)
Lives for festivals, concerts and parties: front row at every show at the park
bandstand, collects festival wristbands, hums along to everything, and is always
trying to drag the others out to a gig or a party. Gag potential: hoof-tapping in quiet places (the post
office, the bus), headbanging gently at the bakery radio, and an episode where
the whole town goes to a concert at the bandstand.

### Dany (Mrs. Marmalade)
The baker. She and Hammi are friends, but he is always a little suspicious of her
because she's a cat: side-eye, narrowed eyes, checking his pastry. He always
caves in the end because he loves her cooking. Running gag: suspicion, sniff,
surrender (ep02 s12/s12a is the first one).

### Vivi
Picky eater who sends dishes back and inspects every crumb, the opposite of Hammi,
who eats anything. Yaps at everything (a visible bark with ears flapping reads
fine without sound). Never seen without a boba milk tea. Natural pairing:
Vivi and Hammi at Dany's bakery or a food festival.

### Jul
Always the hippest animal in the room and overdressed for every occasion:
a puffer jacket at the duck pond, sunglasses at night.
Easy beats: a dramatic outfit reveal, posing for photos, lowering the sunglasses,
judging someone's sweater (Hammi's).

### Molly
Ecstatic about absolutely everything: a new leaf, a bus, a sandwich. Flaps both
wings, hops in place, sparkly eyes. Lives at the duck pond. Good for: big
reactions at reveals and parties, and as the opposite of grumpy-pigeon energy.
Ducks have **two wings and two feet** (no arms), so say so in every prompt.

### Damian
Night-shift doctor at the hospital: sleepy and coffee-dependent by day, first on
the dance floor when off duty. Visually distinct from Professor Hoot (barn owl in
scrubs vs. great horned owl in tweed). Natural pairing: Damian and Toozi as the
party crew.

## The town
- **Pawsley Hollow**: cobblestone streets, autumn trees, scaled-down shopfronts,
  hanging lanterns, a clock tower, a bus stop with a wooden bench.
- Key places: Hammi's cottage, Dany's bakery (sign: "Marmalade's"), the schoolhouse (Hammi's
  class, taught by Professor Hoot, with Pip as a classmate; from ep01 on), the bus route, the park with the duck pond, the
  laundromat.
- **Always autumn** to start with. Seasons make a natural content calendar later
  (a winter arc, a holiday special).

## Episode formula (long-form, ~4–6 min)
1. **Wake-up** (3–4 shots): alarm, stretch, slippers.
2. **Ritual** (4–6 shots): brushing teeth, cereal, toast, washing dishes. No coffee: this is a kids' show.
3. **Out the door** (3–4 shots): scarf on, locking the door, the pigeons watching.
4. **The thing** (8–12 shots): the episode's activity (work, laundromat, baking
   with Dany, a rainy day).
5. **Small problem → small win** (3–5 shots): a dropped letter, a burnt cookie,
   a missed bus.
6. **Wind-down** (4–6 shots): home, tea, the window, lights off.

That's ~30–40 shots at 3–5s each. You can reuse wake-up and wind-down shots
across episodes (and so can the audience, who will start to expect them).

## Shorts formula (15–30s)
One moment, 4–6 shots, with a hook in the first second: "corgi tries to wash
dishes", "POV: your coworker is a hamster", "rainy morning in Pawsley Hollow".
