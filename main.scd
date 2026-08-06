(
s.options.sampleRate = 48000;
s.waitForBoot {



(
//"/Volumes/Ljud 1TB/Supercollider/multiphonics/natalchart.scd".load;
"/Users/roya/Documents/roya/supercollider/natalchart.scd".load;


~birthIntervals = ~intervals[0];
~transitIntervals = ~intervals[1];
~currentIntervals = ~intervals[2];
~transitIntervals.postln;
)

}
)



(
SynthDef(\boundedTone, {
    |out = 0, freq = 400, amp = 0.1|

    var sig;
    var env;

    env = EnvGen.kr(
        Env.perc(0.01, 0.08),
        doneAction: 2
    );

    sig = SinOsc.ar(freq) * env * amp;

    Out.ar(out, sig ! 2);
}).add;
)


(
var seed = 12345;

var center = 400;

var minFreq = 300;
var maxFreq = 500;

var maxStepAtCenter = 20;
var maxStepAtBoundary = 2;

var currentFreq = center;

Pdef(\boundedFrequency,
    Pseed(seed,
        Pbind(
            \instrument, \boundedTone,

            \currentFreq, Pfunc({
                var distance;
                var normalizedDistance;
                var maxStep;
                var change;

                // calculate distance from center
                distance = (currentFreq - center).abs;

                // normalize distance between 0 and 1
                normalizedDistance = distance /
                    ((maxFreq - minFreq) * 0.5);

                normalizedDistance = normalizedDistance.clip(0, 1);

                // distance controls the maximum movement
                maxStep = normalizedDistance.linlin(
                    0, 1,
                    maxStepAtCenter,
                    maxStepAtBoundary
                );

                // seeded pseudorandom movement
                change = rrand(maxStep.neg, maxStep);

                // update frequency and enforce boundaries
                currentFreq = (currentFreq + change).clip(
                    minFreq,
                    maxFreq
                );

                currentFreq;
            }),

            \dur, 0.1,
            \amp, 0.15
        )
    )
);
)


Pdef(\boundedFrequency).play;

Pdef(\boundedFrequency).stop;