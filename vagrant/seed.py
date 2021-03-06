#!/usr/bin/python
from os import remove
from os.path import isfile
from shutil import copytree, rmtree

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog import Base, Category, Item, RELATIVE_IMAGE_DIRECTORY, User


USERS = [
    {
        'id': 1,
        'name': '',
        'email': 'musicshop999@gmail.com',
        'picture': '',
        'group': 'admin'
    }
]


CATEGORIES = [
    {
        'id': 'guitars',
        'name': 'Guitars'
    },
    {
        'id': 'bass',
        'name': 'Bass Guitars'
    },
    {
        'id': 'amplifiers-effects',
        'name': 'Amplifiers & Effects'
    },
    {
        'id': 'drums-percussion',
        'name': 'Drums & Percussion'
    },
    {
        'id': 'live-sound',
        'name': 'Live Sound'
    },
    {
        'id': 'recording-gear',
        'name': 'Recording'
    },
    {
        'id': 'accessories',
        'name': 'Accessories'
    }
]


ITEMS = [
    {
        "category_id": "accessories",
        "description": "The string you need to get the sound you're after, again and again. Gauges 10-13-17-26-36-46. World-renowned as \"The Player's Choice\" among guitarists of all genres and styles. EXL strings are wound with nickel-plated steel, known for it's distinctive bright tone and reduced fret wear. EXL110s are among D'Addario's most popular round-wound, nickel-plated electric guitar strings. D'Addario is the world's largest manufacturer of strings for musical instruments. Many top guitarists won't play any other brand. Regardless of your playing style, D'Addario has a string set that's right for you.",
        "id": "daddario-exl110-nickel-light-electric-guitar-strings-3-pack",
        "image_path": "/img/daddario-exl110-nickel-light-electric-guitar-strings-3-pack-20150925043619.png",
        "name": "D'Addario EXL110 Nickel Light Electric Guitar Strings 3-Pack",
        "price": "$9.99",
        "short_description": "The string you need to get the sound you're after, again and again. World-renowned as \"The Player's Choice\" among guitarists of all genres and styles.",
        "user_id": 1
    },
    {
        "category_id": "accessories",
        "description": "Whether it's the studio or the stage this cable won't let you down. American Stage cables are built to ensure that your tone comes through exactly the way you want it. Planet Waves uses audiophile-quality wire that's made in the USA and designed to reproduce the natural tones of your instrument with zero interference. The plugs are made by Neutrik in their state-of-the-art facility in Lichtenstein in accordance with Planet Waves' patented specs. The exclusive Planet Waves In-Line solder process creates a permanent bond between wire and plug, making a clear connection with incredible strength and durability.",
        "id": "daddario-planet-waves-american-stage-instrument-cable",
        "image_path": "/img/daddario-planet-waves-american-stage-instrument-cable-20150925043735.png",
        "name": "D'Addario Planet Waves American Stage Instrument Cable",
        "price": "$19.95",
        "short_description": "Whether it's the studio or the stage this cable won't let you down. American Stage cables are built to ensure that your tone comes through exactly the way you want it.",
        "user_id": 1
    },
    {
        "category_id": "accessories",
        "description": "Reap the benefits of time-tested Fender quality\r\nGauges: 45-65-85-105. Fender Super 7250M Nickel-Plated Steel (NPS) bass strings combine the high output and dynamic sound of steel with the smooth feel of nickel. Perfect for rock, funk, and other styles of music where the bass needs to cut through. Fender has been an instrument of choice for many of the greatest musicians since 1946. Fender's popularity through the generations is a result of their design innovations and commitment to quality. These medium bass strings reflect this legacy and are worthy of the Fender name. Attention to detail and the finest materials ensure that you will get the best feeling and greatest sounding replacement strings, set after set.",
        "id": "fender-7250m-super-bass-nickel-plated-steel-long-scale-bass-strings-medium",
        "image_path": "/img/fender-7250m-super-bass-nickel-plated-steel-long-scale-bass-strings-medium-20151002230015.png",
        "name": "Fender 7250M Super Bass Nickel-Plated Steel Long Scale Bass Strings - Medium",
        "price": "$16.95",
        "short_description": "Reap the benefits of time-tested Fender quality. Perfect for rock, funk, and other styles of music where the bass needs to cut through.",
        "user_id": 1
    },
    {
        "category_id": "accessories",
        "description": "Lightweight quality drum protection at an affordable price. The Gator GP-Standard-100 5-Piece Padded Standard Drum Bag Set features drum bags constructed of rugged 600-denier nylon. They are heavily padded and lined, providing perfect protection for your drum kit's finish during daily cartage. Comfortable carrying straps. Designed to fit 22\" x 18\" bass; 12\" x 10\" and 13\" x 11\" toms; 16\" x 16\" floor tom; and 5-1/2\" x 14\" snare.",
        "id": "gator-gp-standard-100-padded-5-piece-standard-drum-bag-set",
        "image_path": "/img/gator-gp-standard-100-padded-5-piece-standard-drum-bag-set-20150925043911.png",
        "name": "Gator GP-Standard-100 Padded 5-Piece Standard Drum Bag Set",
        "price": "$139.99",
        "short_description": "Lightweight quality drum protection at an affordable price. 5-Piece Padded Standard Drum Bag Set features drum bags constructed of rugged 600-denier nylon.",
        "user_id": 1
    },
    {
        "category_id": "amplifiers-effects",
        "description": "A bass cab that's ready to hit the road with certified Ampeg tone and style with a kick-ass head to match. Add the PF-500 Portaflex and PF115HE Stack from Ampeg to your road gear and ensure your bass will get all the love it deserves in the mix. Featuring the PF-115HE with it's 15\" Eminence driver and the PF-500 Portaflex with it's 500W of driving power, and you'll be hitting the high road with your low end.",
        "id": "ampeg-pf-500-portaflex-and-pf-115he-stack",
        "image_path": "/img/ampeg-pf-500-portaflex-and-pf-115he-stack-20150925035647.png",
        "name": "Ampeg PF-500 Portaflex and PF-115HE Stack",
        "price": "$799.98",
        "short_description": "A bass cab that's ready to hit the road with certified Ampeg tone and style with a kick-ass head to match.",
        "user_id": 1
    },
    {
        "category_id": "amplifiers-effects",
        "description": "The Blues Jr. NOS takes Fender's 15W gem and gives it the true vintage treatment with tweed covering and a vintage-style 12\" Jensen speaker. Its power is generated by an all-tube signal path using a pair of EL84 Groove Tube output tubes and 3 - 12AX7 preamp tubes. Add renowned Fender reverb, flexible controls, and footswitchable (with optional footswitch - product #420703) FAT circuit for golden tones, and you're in business. And just look at that chrome panel, that tweed finish with pinstripe grille cloth, and those vintage pointer knobs!",
        "id": "fender-blues-junior-lacquered-tweed-15w-1x12-combo",
        "image_path": "/img/fender-blues-junior-lacquered-tweed-15w-1x12-combo-20150925035526.png",
        "name": "Fender Blues Junior Lacquered Tweed 15W 1x12 Combo",
        "price": "$599.99",
        "short_description": "The Blues Jr. NOS takes Fender's 15W gem and gives it the true vintage treatment with tweed covering and a vintage-style 12\" Jensen speaker.",
        "user_id": 1
    },
    {
        "category_id": "amplifiers-effects",
        "description": "After much customer demand, Marshall is offering the most popular product from its Silver Jubilee range. First released in 1987 to celebrate 25 years of Marshall Amplification, and to commemorate Jim Marshall's 50th year in the music industry, the 2555 has become a legendary and much sought-after amplifier due to its distinct looks, sound and features. The 2555X is a modern-day reissue, featuring all of the original panel features found on the 2555, and reproducing its signature tone perfectly.",
        "id": "marshall-2555x-silver-jubilee-100-w-tube-guitar-head",
        "image_path": "/img/marshall-2555x-silver-jubilee-100-w-tube-guitar-head-20150925035802.png",
        "name": "Marshall 2555X Silver Jubilee 100 W Tube Guitar Head",
        "price": "$1899.99",
        "short_description": "After much customer demand, Marshall is offering the most popular product from its Silver Jubilee range.",
        "user_id": 1
    },
    {
        "category_id": "amplifiers-effects",
        "description": "Among the various VOX tube amps, the AC4 has remained one of the most popular over the years, as they provide a simple and hassle free way to enjoy the rich sound of a tube-driven amp. While previous models were equipped with a 10\" speaker, this new model features a 12\" Celestion speaker that delivers even more robust sound levels. With diamond grille cloth and basket-weave vinyl exterior, it also carries on the classic looks of the VOX tradition. This is a Class A tube amp that you can enjoy whether you're practicing at home, performing live, or recording. The AC30's Top Boost sound has fascinated guitarists around the world for over fifty years. Capable of massive crunch or the clean, classic \"chime,\" this Top Boost tone is the essence of VOX's identity. The AC4C1-12 now delivers this unbeatable sound in a portable, compact body. Gain control, Bass and Treble tone controls, and a Master Volume allow any player to easily recreate this historic sound.",
        "id": "vox-ac4c1-12-1x12-classic-limited-edition-tube-guitar-combo-amp",
        "image_path": "/img/vox-ac4c1-12-1x12-classic-limited-edition-tube-guitar-combo-amp-20151002225012.png",
        "name": "Vox AC4C1-12 1x12 Classic Limited Edition Tube Guitar Combo Amp",
        "price": "$349.99",
        "short_description": "A solid 4-watt combo amplifier with a 12\" speaker sure to impress with traditionally VOX sound and design.",
        "user_id": 1
    },
    {
        "category_id": "bass",
        "description": "A bolt-on neck joint on the Ibanez SR505 5-string bass guitar allows superb access to the upper frets of its five-piece jatoba/bubinga neck. Only 4/5\" thick at the first fret, the 34\" scale neck provides more comfortable playing than standard 5-string necks.",
        "id": "ibanez-sr505-5-string-electric-bass-guitar",
        "image_path": "/img/ibanez-sr505-5-string-electric-bass-guitar-20150925035347.png",
        "name": "Ibanez SR505 5-String Electric Bass Guitar",
        "price": "$649.99",
        "short_description": "A bolt-on neck joint on the Ibanez SR505 5-string bass guitar allows superb access to the upper frets of its five-piece jatoba/bubinga neck.",
        "user_id": 1
    },
    {
        "category_id": "bass",
        "description": "Michael Tobias and legendary bassist Andrew Gouche worked together to create the MTD Kingston AG, an amazing bass with many custom features that were personally selected by Andrew himself. This bass is fully loaded with a 35\" scale, alder body with maple burl top and one-piece neck, MTD quick release bridge and Bartolini pickups and active Bartolini 3-band preamp. With its smooth playability and mind altering tones this bass will change the way you think about the instrument. Available in a custom finish created to perfectly blend with the fingerboard.",
        "id": "mtd-kingston-andrew-gouche-signature-6-string-electric-bass",
        "image_path": "/img/mtd-kingston-andrew-gouche-signature-6-string-electric-bass-20150925035145.png",
        "name": "MTD Kingston Andrew Gouche Signature 6-String Electric Bass",
        "price": "$2149.00",
        "short_description": "Michael Tobias and legendary bassist Andrew Gouche worked together to create the MTD Kingston AG, an amazing bass with many custom features that were personally selected by Andrew himself.",
        "user_id": 1
    },
    {
        "category_id": "bass",
        "description": "The Schecter Guitar Research Stiletto Extreme-4 is an electric bass that delivers the ideal combination of hard-hitting Schecter sound and jaw-dropping aesthetics. The Stiletto Extreme-4 bass has a lower-cutaway mahogany body, exquisite figured maple top, maple neck, and 24-jumbo-fret rosewood fingerboard that provide a uniquely awesome playing experience. And for dialing in your ideal sound, the Stiletto Extreme-4 bass's 2 Schecter bass humbucker pickups with active EQ give you maximum control. If you like your sound heavy and your electric bass awe-inspiring, snag the Schecter Stiletto Extreme-4.",
        "id": "schecter-guitar-research-stiletto-extreme-4-bass",
        "image_path": "/img/schecter-guitar-research-stiletto-extreme-4-bass-20151002224827.png",
        "name": "Schecter Guitar Research Stiletto Extreme-4 Bass",
        "price": "$399.99",
        "short_description": "Shake the earth in style with this hot, powerful axe. The Schecter Guitar Research Stiletto Extreme-4 is an electric bass that delivers the ideal combination of hard-hitting Schecter sound and jaw-dropping aesthetics.",
        "user_id": 1
    },
    {
        "category_id": "bass",
        "description": "An affordable short-scale Jaguar Bass with classic Fender style! The all-new Vintage Modified Jaguar Bass Special SS puts classic Fender looks into a distinctively sharp-looking, great-sounding, and super-versatile short-scale Squier bass model.",
        "id": "squier-vintage-modified-jaguar-bass-special-ss-short-scale",
        "image_path": "/img/squier-vintage-modified-jaguar-bass-special-ss-short-scale-20150925042500.png",
        "name": "Squier Vintage Modified Jaguar Bass Special SS (Short Scale)",
        "price": "$179.99",
        "short_description": "An affordable short-scale Jaguar Bass with classic Fender style!",
        "user_id": 1
    },
    {
        "category_id": "drums-percussion",
        "description": "No detail has been overlooked. No corners cut. Its look and sound are custom-inspired. Its value difficult to match. To its makers, the Performance Series exemplifies what it means to be handcrafted by DW. In addition to advanced HVX shell technology devised and constructed by John Good and the DW Custom Shop team in in the USA at their Oxnard, California shop, this Performance Series 5-piece kit is fitted with quarter turret lugs, low mass die-cast claw hooks, and finished in a gorgeous pewter sparkle framed by chrome hardware.",
        "id": "dw-performance-series-5-piece-shell-pack",
        "image_path": "/img/dw-performance-series-5-piece-shell-pack-20150925035916.png",
        "name": "DW Performance Series 5-Piece Shell Pack",
        "price": "$2044.97",
        "short_description": "No detail has been overlooked. No corners cut. Its look and sound are custom-inspired. Its value difficult to match.",
        "user_id": 1
    },
    {
        "category_id": "drums-percussion",
        "description": "Punishing double-kick configuration for drummers who want to lay down a wall of sound. Poplar shells offer a great blend of sustain and punch, and are outfitted with Remo heads as well as attractive black lugs and hoops. 2 - 22\" x 18\" kick drums, 8\" x 7\", 10\" x 8\", and 12\" x 9\" toms, 14\" x 12\" and 16\" x 14\" floor toms, and 14\" x 5-1/2 snare. Cymbals and hardware sold separately.",
        "id": "pdp-double-drive-8-piece-shell-pack",
        "image_path": "/img/pdp-double-drive-8-piece-shell-pack-20150925040142.png",
        "name": "PDP Double Drive 8-Piece Shell Pack",
        "price": "$729.99",
        "short_description": "Punishing double-kick configuration for drummers who want to lay down a wall of sound. Poplar shells offer a great blend of sustain and punch, and are outfitted with Remo heads as well as attractive black lugs and hoops.",
        "user_id": 1
    },
    {
        "category_id": "drums-percussion",
        "description": "Enhanced with SuperNATURAL power, the Roland TD-11KV V-Drums V-Compact Series brings a more natural and realistic playing experience to drummers of any skill level and budget. Affordable and easy to use, this new electronic kit is perfect for a variety of applications, including practice, teaching, recording, live performance, and more.",
        "id": "roland-td-11kv-s-v-compact-series-electronic-drum-kit",
        "image_path": "/img/roland-td-11kv-s-v-compact-series-electronic-drum-kit-20151002225256.png",
        "name": "Roland TD-11KV-S V-Compact Series Electronic Drum Kit",
        "price": "$1599.99",
        "short_description": "Compact and Affordable V-Drums, Powered by SuperNATURAL. Affordable and easy to use, this new electronic kit is perfect for a variety of applications, including practice, teaching, recording, live performance, and more.",
        "user_id": 1
    },
    {
        "category_id": "drums-percussion",
        "description": "Among Yamaha's most affordable 100% birch drum shell packs. This Yamaha Stage Custom birch drum shell pack is also great for the beginner or the working professional. The staggered diagonal seam allowed Yamaha to build a thin drum shell that will start round and stay round. The low-mass lugs lets the shell vibrate for superb tone and sustain. Yamaha's Air Seal System used for drum shell construction ensures each and every Yamaha drum shell is of uniform thickness and is perfectly round to achieve superior tone quality and durability.",
        "id": "yamaha-stage-custom-birch-5-piece-shell-pack-with-22-bass-drum",
        "image_path": "/img/yamaha-stage-custom-birch-5-piece-shell-pack-with-22-bass-drum-20150925040011.png",
        "name": "Yamaha Stage Custom Birch 5-Piece Shell Pack with 22\" Bass Drum",
        "price": "$649.99",
        "short_description": "Among Yamaha's most affordable 100% birch drum shell packs. This Yamaha Stage Custom birch drum shell pack is also great for the beginner or the working professional.",
        "user_id": 1
    },
    {
        "category_id": "guitars",
        "description": "The easy-to-afford dreadnought Epiphone PR-150 is the perfect instrument to get started on. It has classic looks, great tone, and is made to be road tough. Like all worthy acoustic guitars, it begins and ends with tonewoods, and the PR-150 Epiphone chose a select spruce top and mahogany body for a classic sound that's balanced, clear, and will only get better with age and lots of playing. The rosewood bridge and synthetic bone saddle are a perfect match for the resonant profile of the select spruce top. The vintage-style soundhole is supported by a tortoiseshell-style pickguard with the '60s era \"E\" logo. The SlipTaper 25.5\" scale mahogany neck has a rosewood fingerboard with dot inlays, a 12\" radius, a 1.68\" nut, premium die-cast 14:1 tuners, and the classic '60s era Sloped Dovewing headstock. The Epiphone's all-nickel hardware will last as long as you play the guitar and the PR-150 comes in two color finishes, Natural (NA) and Vintage Sunburst (VS). Choose the finish you want in the drop down menu above.",
        "id": "epiphone-pr-150-acoustic-guitar",
        "image_path": "/img/epiphone-pr-150-acoustic-guitar-20150925034301.png",
        "name": "Epiphone PR-150 Acoustic Guitar",
        "price": "$99.99",
        "short_description": "The easy-to-afford dreadnought Epiphone PR-150 is the perfect instrument to get started on.",
        "user_id": 1
    },
    {
        "category_id": "guitars",
        "description": "To honor the 60th anniversary of the Stratocaster in 2014, Fender introduces brilliant new limited-edition looks for the venerable American Standard Stratocaster Vintage White with a tortoiseshell pickguard and rosewood fingerboard. All the acclaimed features, sound and style of the archetypal American Standard Stratocaster, now in an even more beautiful finish.",
        "id": "fender-limited-edition-american-standard-stratocaster-rosewood-fingerboard-electric-guitar",
        "image_path": "/img/fender-limited-edition-american-standard-stratocaster-rosewood-fingerboard-electric-guitar-20150925034151.png",
        "name": "Fender Limited Edition American Standard Stratocaster Rosewood Fingerboard Electric Guitar",
        "price": "$999.99",
        "short_description": "To honor the 60th anniversary of the Stratocaster in 2014, Fender introduces brilliant new limited-edition looks for the venerable American Standard Stratocaster Vintage White with a tortoiseshell pickguard and rosewood fingerboard.",
        "user_id": 1
    },
    {
        "category_id": "guitars",
        "description": "The Gibson 2015 Les Paul Traditional Electric Guitar combines classic features from the '50s along with some key updates for 2015. The mahogany body is unrouted for improved sustain and has a figured maple top in a choice of delicious colors. Highlights include a late '50s contour mahogany neck, bound rosewood fingerboard, '59 Tribute humbuckers with orange drop capacitors, and a gloss lacquer body finish. Includes hardshell case.",
        "id": "gibson-2015-les-paul-traditional-electric-guitar",
        "image_path": "/img/gibson-2015-les-paul-traditional-electric-guitar-20150925040736.png",
        "name": "Gibson 2015 Les Paul Traditional Electric Guitar",
        "price": "$2447.00",
        "short_description": "The Gibson 2015 Les Paul Traditional Electric Guitar combines classic features from the '50s along with some key updates for 2015.",
        "user_id": 1
    },
    {
        "category_id": "guitars",
        "description": "Dual humbuckers and a semi-hollow ash body provide distinctive sound and personality. Squier's Vintage Modified '72 Telecaster Thinline evokes the popular second incarnation of that era's stylishly enlightened Tele model. The original late-'60s version, with its two single-coil pickups, was updated in 1972 with two great-big, great-sounding Wide Range humbucking pickups for an even more distinctive sound and personality, and that's exactly what Squier gives you here, along with a gorgeous semi-hollow ash body and white pearloid pickguard, smooth-playing maple neck and fingerboard, six-saddle string-through-body bridge and much more.",
        "id": "squier-vintage-modified-72-telecaster-thinline-maple-neck-electric-guitar",
        "image_path": "/img/squier-vintage-modified-72-telecaster-thinline-maple-neck-electric-guitar-20151002224533.png",
        "name": "Squier Vintage Modified 72 Telecaster Thinline Maple Neck Electric Guitar",
        "price": "$299.99",
        "short_description": "Squier's Vintage Modified '72 Telecaster Thinline evokes the popular second incarnation of that era's stylishly enlightened Tele model.",
        "user_id": 1
    },
    {
        "category_id": "live-sound",
        "description": "The frequency range and crossover of the TRUESONIC TSSUB18 has been tuned to provide smooth, low-end sound production in the 37Hz-125Hz range. It also offers stereo inputs, an internal active crossover, and is housed in a rugged, compact, 18mm birch plywood cabinet with durable metal recessed handles. When you're ready to extend the frequency range of your live performance reinforcement, a TRUESONIC TSSUB18 subwoofer is an effective, economical, and professional choice.",
        "id": "alto-tssub18-18-1200w-peak-active-subwoofer",
        "image_path": "/img/alto-tssub18-18-1200w-peak-active-subwoofer-20151002225459.png",
        "name": "Alto TSSUB18 18\" 1200W Peak Active Subwoofer",
        "price": "$699.99",
        "short_description": "Affordable 18\" powered subwoofer with Class D power. Exacting details were planned and provided in the TRUESONIC TSSUB18.",
        "user_id": 1
    },
    {
        "category_id": "live-sound",
        "description": "Gem Sound's PXA Series powered speakers provide an inexpensive sound reinforcement solution that satisfies all of the chief requirements for a powered speaker. The USB series additionally provides a direct connection to your digital music library, either via SD cards or direct input from your USB devices. This is the PXA115T-USB, a 300-watt powered enclosure with a 15\" woofer and a 1\" high frequency compression driver. It additionally features a small input section that enables you to perform or make your presentations using just the PXA115T-USB without any other equipment at all. Just plug in your microphone and your guitar or keyboard and go. You can independently control two channels at the input stage, and you can shape the sound with an onboard five-band equalizer.",
        "id": "gem-sound-pxa115t-usb-15-powered-speaker-pair",
        "image_path": "/img/gem-sound-pxa115t-usb-15-powered-speaker-pair-20150925040332.png",
        "name": "Gem Sound PXA115T-USB 15\" Powered Speaker Pair",
        "price": "$699.98",
        "short_description": "Gem Sound's PXA Series powered speakers provide an inexpensive sound reinforcement solution that satisfies all of the chief requirements for a powered speaker.",
        "user_id": 1
    },
    {
        "category_id": "live-sound",
        "description": "An 18\" sub with 1000 Class D continuous output, and extended bass in a lighter birch enclosure. Building on the success of QSC's K Series, the KW181 subwoofer, like the rest of QSC's KW active loudspeakers, represents QSC's next evolutionary step in wood enclosure loudspeakers. The system engineers created the KW series to feature all the groundbreaking electronic attributes of the popular K Series while at the same time designing a product that is both smaller and significantly lighter than previous wood enclosure models.",
        "id": "qsc-kw181-powered-sub-woofer-18-1000w",
        "image_path": "/img/qsc-kw181-powered-sub-woofer-18-1000w-20150925040443.png",
        "name": "QSC KW181 Powered Sub Woofer 18\" 1000W",
        "price": "$1399.00",
        "short_description": "An 18\" sub with 1000 Class D continuous output, and extended bass in a lighter birch enclosure.",
        "user_id": 1
    },
    {
        "category_id": "live-sound",
        "description": "These Yamaha S115V Club Series V Speakers are all about big house sound. Gigging bands, mobile DJs, and houses of worship helped make the first 4 generations of Yamaha Club Series audio speakers incredibly popular. The refinements of generation V continue this success story with larger enclosures for improved low-frequency performance, improved drivers for higher power handling, redesigned crossovers, stronger grilles, and dual Speakon and 1/4\" connectors. With professional features, excellent sonic performance, and great value, Club Series loudspeakers deliver premium quality night after night.",
        "id": "yamaha-s115v-2-way-15-club-series-v-speaker-pair",
        "image_path": "/img/yamaha-s115v-2-way-15-club-series-v-speaker-pair-20150925040631.png",
        "name": "Yamaha S115V 2-Way 15\" Club Series V Speaker Pair",
        "price": "$759.98",
        "short_description": "These Yamaha S115V Club Series V Speakers are all about big house sound.",
        "user_id": 1
    },
    {
        "category_id": "recording-gear",
        "description": "Distinctive sound with a stylish look. Engineered for meticulous reproduction of even the most complex modern music, Akai Professional's RPM500 studio monitors easily handle layer after layer of sound, providing critical detail and the tools needed to mix with confidence. The fast Kevlar cone provides lucid low-end agility, reproducing intricate bass patterns with ease. It's authoritative sound for the craft of music production, only from Akai Professional.",
        "id": "akai-professional-rpm500-black-studio-monitor",
        "image_path": "/img/akai-professional-rpm500-black-studio-monitor-20150925042919.png",
        "name": "Akai Professional RPM500 Black Studio Monitor",
        "price": "$149.00",
        "short_description": "Distinctive sound with a stylish look. Engineered for meticulous reproduction of even the most complex modern music, Akai Professional's RPM500 studio monitors easily handle layer after layer of sound, providing critical detail and the tools needed to mix with confidence.",
        "user_id": 1
    },
    {
        "category_id": "recording-gear",
        "description": "Recording package with interface, monitors, mic and more. We've put together this recording package to make it easy for you to get the essential components you need with just one purchase, and at a price that's much more affordable than if you purchased everything individually. Included in this package is the Focusrite Scarlett 2i2 USB Audio Interface, a pair of Alesis Elevate 3 studio monitors, a pair of AKG M80 MKII Headphones, an MXL 990 condenser microphone, and all the accessories and cables you need to get set up.",
        "id": "focusrite-scarlett-2i2-mxl-990-package",
        "image_path": "/img/focusrite-scarlett-2i2-mxl-990-package-20150925042749.png",
        "name": "Focusrite Scarlett 2i2 MXL 990 Package",
        "price": "$349.99",
        "short_description": "Recording package with interface, monitors, mic and more. We've put together this recording package to make it easy for you to get the essential components you need with just one purchase, and at a price that's much more affordable than if you purchased everything individually.",
        "user_id": 1
    },
    {
        "category_id": "recording-gear",
        "description": "The Mackie Control Universal Pro is a control surface made to give you tactile control over all the parameters of your computer recording software. Since it employs the proprietary Mackie communication protocol, Mackie Control Pro Series controllers know just how to sweet-talk your software, and your software knows just how to respond. You get deep, intuitive control of mix and plug-in parameters, realtime visual feedback, and setup is plug and play-no MIDI mapping head games! The Universal Pro control surface, Extender Pro control surface extension and C4 Pro plug-in and virtual instrument controller all seamlessly integrate, so you can put control of all your music software parameters right at your fingertips. Simply put, Mackie Control Pro Series controllers give your music production software what it needs to feel complete.",
        "id": "mackie-control-universal-pro",
        "image_path": "/img/mackie-control-universal-pro-20151002225710.png",
        "name": "Mackie Control Universal Pro",
        "price": "$1099.99",
        "short_description": "Premium hands-on control of your music software. Simply put, Mackie Control Pro Series controllers give your music production software what it needs to feel complete.",
        "user_id": 1
    },
    {
        "category_id": "recording-gear",
        "description": "Two-way bass-reflex bi-amplified nearfield studio monitor with 8\" cone. The Yamaha HS8 is a 2-way bass-reflex bi-amplified nearfield studio monitor with 8\" cone woofer and 1\" dome tweeter. The Yamaha HS-Series have the inherited universal mix-translation legacy and distinctive white cones of the industry-respected NS-10's, designed to deliver your mixes with transparent honesty. Room control and frequency response switches allow custom tailoring of the monitor's response to give you accurate performance in any environment.",
        "id": "yamaha-hs8-powered-studio-monitor",
        "image_path": "/img/yamaha-hs8-powered-studio-monitor-20150925043334.png",
        "name": "Yamaha HS8 Powered Studio Monitor",
        "price": "$349.99",
        "short_description": "Two-way bass-reflex bi-amplified nearfield studio monitor with 8\" cone. The Yamaha HS8 is a 2-way bass-reflex bi-amplified nearfield studio monitor with 8\" cone woofer and 1\" dome tweeter.",
        "user_id": 1
    }
]


# Copy seed images to img.
rmtree('img', ignore_errors=True)
copytree('seed_images', RELATIVE_IMAGE_DIRECTORY)

# Remove catalog.db, if exists.
if isfile('catalog.db'):
    remove('catalog.db')

# Create the database.
engine = create_engine('sqlite:///catalog.db')
# engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.create_all(engine)
db_session = sessionmaker(bind=engine)
catalog = db_session()

# Add users to the database.
for user in USERS:
    catalog.add(User(name=user['name'],
                     email=user['email'], picture=user['picture'],
                     group=user['group']))

# Add categories to the database.
for category in CATEGORIES:
    catalog.add(Category(id=category['id'], name=category['name']))

# Add items to the database.
for item in ITEMS:
    catalog.add(
        Item(id=item['id'], name=item['name'],
             short_description=item['short_description'],
             description=item['description'], price=item['price'],
             image_path=item['image_path'],
             category_id=item['category_id'],
             user_id=item['user_id']))

# Commit all the database changes.
catalog.commit()
