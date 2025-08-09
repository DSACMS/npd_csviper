There is a ruby-based csvlint command line tool available from https://github.com/Data-Liberation-Front/csvlint.rb

It should be installed with brew, etc and work from the command line. The readme should say that this is required but and link to https://github.com/Data-Liberation-Front/csvlint.rb for installation instructions.

brew install ruby && gem install bundler csvlint

Which needs to be a step added to the ReadME.md

The python command should see if the linter is present, and if it is not, it should stop running until it works on the command line.

When compiling the CSV approach, csvlint should be run on every file.

And if the csvlint command says there is an error, the import/compile should not be attempted and an error should be thrown.

The output of csvlint is like

```bash
good_file.csv is VALID
1. this is a warning
```

or

```bash
bad_file.csv is INVALID
1. this is the error
```

csvlint also makes warnings. These warnings can be ignored, unless they are:

* :empty_column_name
* :duplicate_column_name
* :title_row

Which should be treated as errors in this project.

At both the compile and import stages, using csvlint should be the default.
There should be a command line flag called --no_csv_lint that will cause the linter stage to be skipped.
If the csvlinter stage is skipped obviously the system should not crash if csvlinter ins not installed.
