# lab-wiki-builder
a tool for building wiki websites for academic labs based on GitHub pages.

## motivation

As academic labs grow, projects and people come and go. PIs cannot track everything only by memory,
and students often have difficulty sharing resources together. Consider the following scenarios.

1. **Difficulty running legacy projects** John left three years ago and he left quite a lot of unorganized code in
   his computer. Mary wants to continue John's work, yet she has great difficulty in running John's programs.
   She resorts to asking John by email, yet he has forgotten many details in his old work,
   and he is also too busy with his new life to reply. Mary gets frustrated, and the PI feels that Mary's progress is
   slower than expected.
2. **Reinventing the wheel** John and Mary work on similar yet different projects. They both need a nonexistent MATLAB
   (replace it with your favorite language, though I think such scenario is more common for MATLAB) function to solve
   the same problem, and they decide to write their own versions. As they are not CS professionals, and there is little
   reference to be found on this function over the Internet,
   both of their functions have different bugs unknown to themselves, and more
   time is spent on inventing the (actually crappy) wheels than what's necessary.
3. **Unable to share knowledge across generations** John is a genius on some little-known topic X,
   and he has many original yet unpublished insights on this topic.
   Mary is asked by the PI to work on X, yet she feels lost when reading all the obscure papers on this topic.
   She wants guidance from John, yet he is far away and unreachable. In the end, Mary spends much time rereading all the
   papers that John has already read long ago, before she can make any new progress.

Solving the above problems requires combined efforts from both the PI and students, and this tool helps reducing the
logistic overheads of lab management in the following aspects.

1. Allowing knowledge sharing among students by building a **reference library** in a tree-like structure.
2. Allowing finding projects and computing resources easily by building a **project library**,
   which includes research projects as well as toolbox ones.
  
In addition, [this page](https://rrcns.readthedocs.io) gives a set of reasons
for the necessity of doing all the "non-science" management stuffs, specifically for neurophysiology labs.

## demos

* [Demo reference library](https://leelabcnbc.github.io/lab-wiki-builder/demo_ref/)
* [Demo project library](https://leelabcnbc.github.io/lab-wiki-builder/demo_proj/)

## how to use it.

~~~
usage: lab_wiki_builder.py [-h] (--ref | --proj) input [output]

build lab wiki website.

positional arguments:
  input       the root directory of library source files.
  output      the root directory of library output files. If not set, it will
              be equal to `input`.

optional arguments:
  -h, --help  show this help message and exit
  --ref       build reference library.
  --proj      build project library.
~~~

## how it works

It's actually quite simple.

1. Go through every **eligible** folder under `INPUT`.
    * `eligible` means the following. Suppose a folder is `INPUT/A/B/C`, then
       1. Starting from root, each level (`A`,`B`,`C`) must only contain digits,
          lowercase letters, or `_`, and must not start with `_`.
2. Under each eligible folder, we will scan every **entry file** to collect information needed for library building.
    * `entry file` means different things for different building options.
       1. for `--ref`, it means all `.ipynb` files
       2. for `--proj`, it means all the `.md` files.
    * the entry files should only have letters, digits, `_` and `-` in their names,
      and their extensions must be lowercase.
3. Using all the collected information, the program builds the library.

