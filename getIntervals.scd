(
// birth data
~year = 1976;
~month = 2;
~day = 23;
~hour = 11;
~minute = 55;
~utcOffset = -8;

// interval mapping
~conjunction = 1/1;
~sextile = 5/3;
~square = 3/2;
~trine = 5/4;
~opposition = 4/3;


~python = "/Users/roya/Documents/roya/supercollider/syntony/chart.py";

~cmd = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 % % % % % % % % % % % %".format(
    ~python,
    ~year,
    ~month,
    ~day,
    ~hour,
    ~minute,
    ~utcOffset,
    ~conjunction,
    ~sextile,
    ~square,
    ~trine,
    ~opposition
);

~result = ~cmd.unixCmdGetStdOut;

~intervals = ~result.interpret;

~intervals.postln;
)

