# ADG - Automatic Diagram Generator

## Description
ADG is a tool generating diagrams and producing their expressions for given
many-body formalisms. Diagrammatic rules from the formalism are combined with
graph theory objects to produce diagrams and expressions in a fast, simple and
error-safe way.

The only input consists in the theory and order of interest, and the N-body
character of the operators of interest. The main output is a LaTeX file
containing the diagrams, their associated expressions and additional
informations that can be compiled by ADG id needed. Other computer-readable
files may be produced as well.

## Status
As for now, the code is capable of handling two different formalisms, i.e.
Many-Body Perturbation Theory (MBPT) and Bogoliubov Many-Body Perturbation
Theory (BMBPT).
  - For MBPT, the code generates all Hartree-Fock energy diagrams at any given
    order along with their expression and additional information
    (conjugate diagram, excitation level...).
  - For BMBPT, the code generates all diagrams for a generic observable
    commuting with the Hamiltonian, along with their time-dependent and
    time-integrated expressions.

## Future developments
Extensions under discussions are diagrams and expressions for Particle-Number
Restored BMBPT as well as diagrams and expressions generation for Gorkov
Self-Consistent Green's Functions (GSCGF).

## Install
To install ADG, download the source files and run
```
pip2 install <project_folder>
```
or alternatively
```
python2 setup.py install
```
If you want to install ADG in ```develop``` mode, then run
```
pip2 install -e <project_folder>
```

## Dependencies
In order to run the code, you will need a Python install >= 2.7.1
  - Python libraries:
  	* networkx >= 2.0
    * numpy
    * scipy

If you want ADG to compile the LaTeX output file, you will need a Latex install
with the PDFLaTeX compiler and the feynmp and feynmp-auto packages installed,
which are standard packages in most recent distributions.


## Use
To run the program and generate BMBPT diagrams at order 4 for example, use
```
adg -o 4 -t BMBPT -d -c
```
where the ```-o``` flag is for the order, ```-t``` for the type of theory,
```-d``` indicates you want the diagrams to be drawn and ```-c``` that you want
ADG to compile the LaTeX output.

You can alternatively run the program in interactive mode by typing
```
adg -i
```

Finally, to obtain more information on all the available flags, use
```
adg -h
```

## Package structure

The main folder contains the README file of the package and the setup.py file
used for installing the package.

### adg folder

This folder contains the various Python files with the functions used by ADG.

### doc folder

This folder contains the documentation of the package in reStructuredText,
as well as the Makefile and the conf.py files used by Sphinx for an automatic
generation of the documentation. Part of the documentation is stored in the adg
subfolder.

The compiled documentation is stored in the build subfolder, in a folder named
after the type of documentation. Especially, the manpages of ADG distributed
with the package are stored in the subfolder /build/man.

### examples folder

This folder contains very simple scripts that can be used to launch test
calculations automatically. The precompiled output corresponding to the tests is
available in the sample_output subfolder, then organized in the same way an
actual calculation output would be stored.

## Citing
If you use ADG in your research work, we kindly ask you to cite the following
paper: []

## License
ADG is licensed under GNU General Public License version 3 (see LICENSE.txt)
```
Copyright (C) 2018 ADG Dev Team
Pierre Arthuis - Irfu, CEA, UPSaclay & CEA/DAM/DIF
Thomas Duguet - Irfu, CEA, UPSaclay & KU Leuven, IKS
Jean-Paul Ebran - CEA/DAM/DIF
Raphaël-David Lasseri - IPN, CNRS/IN2P3, UPSud, UPSaclay
Alexander Tichai - ESNT, Irfu, CEA, UPSaclay
```
