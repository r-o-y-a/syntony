(
s.options.sampleRate = 48000;
s.waitForBoot {


	"/Users/roya/Documents/roya/SuperCollider/syntony/getRelationships.scd".load;

	// data format: name, aspect numerator, aspect denominator, numerator/denominator, orb, angular separation
	~birthRelationships = ~relationships[0];
	~transitRelationships = ~relationships[1];
	~currentRelationships = ~relationships[2];

	// 81 possible pairs (9 x 9)
	//~transitRelationships.size.postln;

	~transitRelationships.do { |r|
		var name = r[0];
		var numerator = r[1];
		var denominator = r[2];
		var ratio = r[3];
		var orb = r[4];
		var angle = r[5];

		// r.postln;
		//[name, numerator, denominator].postln;
	};


	// dictionary of unique denominators ("families")
	~denominators = Dictionary.new;
	~transitRelationships.collect(_[2]).as(Set).do { |d|
		var g = ~transitRelationships.select { |x| x[2] == d };
		~denominators[d] = (
			numerators: g.collect(_[1])
		);

	};


	~families.postln;

	~buf = Buffer.read(s, "/Users/roya/Desktop/temp/bowed_bass.wav");


	// play buffer silently to extract data
	~x = {

		var in;
		var freq, conf, windowSize = 1024;

		in = PlayBuf.ar(2, ~buf, BufRateScale.kr(~buf), loop: 1);

		# freq, conf = FluidPitch.kr(in, windowSize: windowSize);
		//[freq, conf].poll(10, \fluidpitch, conf > 0.99);

		Silent.ar(2);

	}.play;


	SynthDef(\tone, { | freq = 400, pitchDev = 1, amp = 0 |

		var sinosc, sum = 0;

		// set number of harmonics to create
		2.do { | count |
			sinosc = SinOsc.ar(freq * (count + 1) * LFNoise1.kr(Rand(1, 2) ! 2).range(pitchDev.reciprocal, pitchDev));

			//sinosc = sinosc * LFNoise1.kr(Rand(0.05, 8) ! 2).exprange(0.01, 1);

			sum = sum + sinosc;
		};

		sum = sum * 0.05;
		sum = sum * Lag3.kr(amp, 1);

		Out.ar(0, sum);
	}).add;



	// TODO: create multiple synths



	(
		~amp = 0.3;

		~synths = 5.collect {
			Synth(\tone, [
				\freq, 200 * rrand(0.98, 1.02),
				\amp, ~amp
			]);
		};



		Tdef(\dynamics, {
			loop {

				// mostly low/mid dynamics, loud values are rarer
				~amp = rrand(0.0, 1.0).squared;

				// 5% chance of total silence
				if(0.05.coin) {
					~amp = 0;
				};

				~synths.do { |synth|
					synth.set(\amp, ~amp);
				};

				rrand(1.0, 4.0).yield;
			}
		}).play;

	)



}
)

~x.free;




