(
s.options.sampleRate = 48000;
s.waitForBoot {


	"/Users/roya/Documents/roya/supercollider/syntony/getIntervals.scd".load;

	// aspect name, harmonic, orb, angle
	~birthRelationships = ~relationships[0];
	~transitRelationships = ~relationships[1];
	~currentRelationships = ~relationships[2];
	~transitRelationships[0][1].postln;



	~buf = Buffer.read(s, "/Users/roya/Desktop/temp/bowed_bass.wav");



	SynthDef(\tone, { | freq = 400, dev = 1.02, amp = 0 |

		var sinosc, sum = 0;

		2.do { |count|
			sinosc = SinOsc.ar(
				freq * (count + 1) * LFNoise1.kr(Rand(0.05, 0.2) ! 2).range(dev.reciprocal, dev));

			sinosc = sinosc * LFNoise1.kr(Rand(0.05, 8) ! 2).exprange(0.01, 1);

			sum = sum + sinosc;
		};

		sum = sum * 0.05;
		sum = sum * Lag3.kr(amp, 1);

		Out.ar(0, sum);
	}).add;



	~x = {

		var in;
		var freq, conf, windowSize = 1024;

		in = PlayBuf.ar(2, ~buf, BufRateScale.kr(~buf), loop: 1);

		# freq, conf = FluidPitch.kr(in, windowSize: windowSize);
		//[freq, conf].poll(10, \fluidpitch, conf > 0.99);

		Silent.ar(2);

	}.play;



	// TODO: code here to create multiple synths with the calculated frequencies from ~transitIntervals

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




