# OOPSLA'18 Artifact Evaluation

- Title: Reconciling High-level Optimizations and Low-level Code with Twin Memory Allocation

# Getting Started

## Prerequisite

- Ubuntu 16.04 (recommended)
- cmake, g++ (required to compile LLVM/Clang)
- gfortran: (required to run SPEC CPU 2017)
- python 2.7, python-dev, virtualenv, bison, tclsh (required to run LLVM Nightly Tests)
- SPEC CPU2017

## Compiling Clang

This section describes how to compile Clang. Compiling Clang may take more than 30 minutes (for each version).

1. Clone LLVM by running `./clone-base.sh`

2. Compile baseline LLVM by running `./build-clang.sh base <# of cores to use>`

3. Compile LLVM with optimization `inttoptr(ptrtoint(p)) -> p` disabled, by running `./apply-patch.sh 1.nointptrfold` followed by `./build-clang.sh nointptrfold <# of cores to use>`.

4. Compile sound LLVM (represented in 5. Implementation in the paper), by running `./apply-patch.sh 2.soundimpl` followed by `./build-clang.sh soundimpl <# of cores to use>`.

5. Compile sound LLVM with psub instruction added, by running `./apply-patch.sh 3.psub` followed by `./build-clang.sh psub <# of cores to use>`.

6. Compile sound LLVM with optimizations added, by running `./apply-patch.sh 4.optimized` followed by `./build-clang.sh optimized <# of cores to use>`.

## Compiling Rust

This section describes how to compile Rust. Compiling Rust may take more than an hour. Compiling Rust is only required to reproduce miscompilation bugs, but not used to get performance numbers.

1. Clone Rust by running `git clone https://github.com/rust-lang/rust.git`

2. Copy `config.toml.example` into `config.toml`. Update `prefix` variable to your own path, and set `extended` to true.

3. Run `./x.py build ; ./x.py install`. This will build baseline Rust.

4. To build Rust with LLVM having pointer equality propagation disabled, copy `src/llvm` directory from the baseline Rust directory (which will be created during `./x.py build`) into somewhere else.

5. Apply patch `patches/noptreqonly.patch` into the copied LLVM. Applying the patch can fail, but the patch is small so you can easily adjust it.

6. Compile the patched LLVM. You can use `build-llvm.sh <LLVM dir (absolute path)> <LLVM installation dir> <# of cores to use>`.

7. Clone another Rust. Again copy `config.toml.example` into `config.toml`, update `prefix`, `extended` variable as well as `llvm-config`. `llvm-config` should point to `llvm-config` executable file created after building patched LLVM. 

8. Run `./x.py build; ./x.py install`.


# Step by Step Instructions

## Reproducing Miscompilation Bugs (Section 1, Appendix A&B)

`miscompilations` directory contains source files which show miscompilation bug of GCC/LLVM/Rust as depicted in 1. Introduction of this paper.

There are two subdirectories:

1. `cbug`, which is equivalent to the one in Appendix A.,

2. `rustbug`, which is equivalent to the one in Appendix B.

Each subdirectory contains `run.sh` - it will show what the correct answer should be, and what the execution of the source files compiled by baseline compiler as well as our sound LLVM prints.

In case of `cbug`, your gcc may not raise miscompilation, unlike our paper's claim. You can check that gcc indeed raises miscompilation from [here](https://wandbox.org/permlink/kpaCpMzCDopuI0NY) as well.

Before running `rustbug/run.sh`, please update PATH so `cargo` (which is Rust's package manager) can be correctly executed. Please check that baseline Rust raises miscompilation, and Rust with our patch applied produces correct output. If baseline Rust does not raise miscompilation, sometimes it is enough to reorder definition of variables x and y in foo/src/lib.rs. Or, you can see `rustbug` from [here](https://play.rust-lang.org/?gist=4af37285ff8f602a06e402d2bed74f8e&version=stable&mode=release) as well.


## Getting Performance Numbers of SPEC CPU 2017 (Section 6.2)

SPEC CPU 2017 is proprietary, so it is not included in this repository.

A configuration file which is used by SPEC CPU 2017 is in `speccpu2017-config/` directory. The configuration file is based on `Example-clang-llvm-linux-x86.cfg`, which is one of basic configuation files of SPEC CPU 2017.

Before using it, set `BASE_DIR` as well as `LLVM_PATH` variables in the config file.

Here is the list of benchmarks we used, because they contain C/C++ source:
500.perlbench\_r, 502.gcc\_r, 505.mcf\_r, 520.omnetpp\_r,
523.xalancbmk\_r 525.x264\_r 531.deepsjeng\_r   541.leela\_r,
557.xz\_r 508.namd\_r 510.parest\_r 511.povray\_r 519.lbm\_r,
526.blender\_r 538.imagick\_r 544.nab\_r,
507.cactuBSSN\_r 521.wrf\_r 527.cam4\_r

Run `runcpu --config <config.file> --noreportable --rebuild --iterations 3 <benchmark>` to test each benchmark.

If 510.parest\_r raises compilation error, please add following lines into the configuration file after `# Benchmark-specific portability`:

```
510.parest_r:
   PORTABILITY   = -std=c++03
```

After running the 19 benchmarks, use the `result` directory in SPEC CPU 2017 to gather the running time result. You can use python scripts in `speccpu2017-result/` to create .csv file. `speccpu2017-result/` already contains the `result` directories our 3 machines have generated, as well as .csv files. They match the graphs in the paper.


## Getting Performance Numbers of LLVM Nightly Tests (Section 6.2)

First of all, run `./clone-nightlytests.sh` to get LLVM Nightly Tests from LLVM mirror repo.

Next, you should create a Python sandbox. Type `virtualenv2 <any-dir>/mysandbox`.

Install Nightly Tests on the sandbox, by running `<dir>/mysandbox/bin/pip install six==1.10.0; <dir>/mysandbox/bin/pip install typing; <dir>/mysandbox/bin/python lnt/setup.py develop`.

After Nightly Tests is successfully installed you can run `./lnt-run.sh <any-dir>/mysandbox <LLVM-to-run(base/soundimpl/optimized)> <core#>`. If you want to estimate performance, <core#> should be 1.

After running `lnt-run.sh` 3 times, you can make a result table using `lnt-result/parse.py <mysandbox dir> cc.csv rt.csv`.


## Getting # of instructions (Table 1)

This process counts # of important instructions, as depicted in Table 1.
Note that the numbers may differ according to which C/C++ standard library you're using/SPEC CPU2017 minor version/etc., so please check whether the trend of the numbers is equivalent to the one in the paper rather than exact numbers.

### Build instcounter.

Go to directory `instcounter`, and run `./build.sh`.

### Get LLVM IR bitcode files before optimizations

#### LLVM Nightly Tests

Run `./run-lnt-savetemps.sh <sandbox dir> <LLVM version to build(base/nointptrfold/soundimpl/psub)> <core#>`.

This will create \*.bc files inside `<sandbox dir>/<recent test-... dir>/(subdir)`.
 
Run `instcounter/count-sum.sh <sandbox dir>/<the test-... dir>` to get the total # of instructions
generated by Clang frontend, while compiling Nightly Tests.

#### SPEC CPU2017

Please add `-save-temps` into COPTIMIZE/CXXOPTIMIZE so it looks like following:

```
default=base:
    COPTIMIZE     = -O3 -save-temps -mavx
    CXXOPTIMIZE   = -O3 -save-temps -mavx
```

And run SPEC CPU2017 as did before.

Now you should gather generated IR files. They have \*.bc extension. You can gather
them by running `instcounter/copy-spec-beforeopt.sh <destination-dir> <SPEC2017 dir>`
(both should be absolute paths).

You can run `instcounter/count-sum.sh <.bc file-aggregated dir>` and get the total # of instructions
generated by Clang frontend.


### Get LLVM IR bitcode files after optimizations

#### LLVM Nightly Tests

Run `./run-lnt-emitllvm.sh <sandbox dir> <LLVM version to build(base/nointptrfold/soundimpl/psub)> <core#>`.

This will create \*.llvm.o files inside <sandbox dir>/<recent test-... dir>/(subdir). Rename all \*.llvm.o files into \*.ll, and compile them into \*.bc file using `llvm-as` command.

Now you can use `instcounter/count-sum.sh <.bc file-aggregated dir>` again.

#### SPEC CPU2017

Please add `-S -emit-llvm` into COPTIMIZE/CXXOPTIMIZE so it looks like following:

```
default=base:                              
    COPTIMIZE     = -O3 -S -emit-llvm -mavx
    CXXOPTIMIZE   = -O3 -S -emit-llvm -mavx
```

And run SPEC CPU2017 as did before.

Now you should gather generated IR files. They have \*.o extension. You can gather
them by running `instcounter/copy-spec-afteropt.sh <destination-dir> <SPEC2017 dir>`
(both should be absolute paths). And then, rename all \*.o files into \*.ll, and
compile them into \*.bc file using `llvm-as` command.

When \*.bc files are ready, now you can run `instcounter/count-sum.sh <.bc file-aggregated dir>`
and get the statistics.


## Getting Statistics of GVN's replacement (Section 6.2)

This process counts # of replacements based on equality comparison which are done by GVN.
Note that the numbers may differ according to which C/C++ standard library you're using/SPEC CPU2017 minor version/etc., so please check whether the trend of the numbers is equivalent to the one in the paper rather than exact numbers.

### Build Clang with Enhanced Statistics

Compile LLVM with GVN statistics, by running `./apply-patch.sh gvnstat` followed by `./build-clang.sh gvnstat <# of cores to use>`.

### LLVM Nightly Tests

Run `./lnt-run-stats.sh <sandbox dir> <core #>`.

It will create a new `<test-....-..>` directory inside mysandbox. Run `gvnstat/sum-stats-lnt.sh <test-.. absolute path>` to get the statistics.

### SPEC CPU2017

Please add `-mllvm -stats` into COPTIMIZE/CXXOPTIMIZE so it looks like following:

```
default=base:                              
    COPTIMIZE     = -O3 -mllvm -stats -mavx
    CXXOPTIMIZE   = -O3 -mllvm -stats -mavx
```

And run SPEC CPU2017 as did before.

Statistics will be recorded in `results/CPU2017*.log`. You can gather
them by running `gvnstat/sum-stats-spec.sh <absolute path of results dir>`.

