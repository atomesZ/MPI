# Algorithmique répartie
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Generic badge](https://img.shields.io/badge/open_mpi-v4.1.0-blue.svg)](https://www.open-mpi.org/software/ompi/v4.1/)
[![Generic badge](https://img.shields.io/badge/mpi4py-v3.1.1-orange.svg)](https://mpi4py.readthedocs.io/en/stable/)

Nous souhaitons mettre en place un système clients/serveurs avec un mécanisme permettant de contrôler ou d’injecter des fautes dans le système. L’idée générale est la suivante : les clients proposent des valeurs/commandes aux serveurs. Ces serveurs souhaitent ensuite se mettre d’accord sur l’ordre dans lequel ils vont accepter ces commandes. Une fois d’accord, il les écriront dans un fichier de log. Chaque serveur doit, à la fin de l’execution, avoir le même fichier de log. Il s’agit donc d’une forme de réplication de logs.

## Pré-requis
**MPI doit être installé au préalable sauf si vous utilisez la version Dockerisée de ce projet**  
Site : https://www.open-mpi.org/software/ompi/v4.1/

Ou sur un Ubuntu/Debian : `sudo apt install libopenmpi-dev -y`

## Installation et démarrage
Pour lancer le projet : `make`  

### Testsuite
Pour lancer la testsuite : `make check`  
Elle vérifie que les commandes des clients soient bien tous receptionnés et que log serveurs soient bien tous identiques. Le REPL doit recevoir la commande `END` avant que le résultat de la testsuite s'affiche.  

### Docker
Si vous souhaitez le run dans un docker :  
Build l'image : `docker build -t mpi_project .`  
Run le container en mode interactif : `docker run --rm -it mpi_project`

Vous pouvez donc ensuite run les différentes commandes du Makefile qui y sont documentés.

### Debug
Pour lancer le debug : `make debug`  
Affiche les étapes intermédiaires :
* Changement d'état d'un serveur (Candidat/Follower/Leader, Crash/Recovery) et de leur Time out
* Envoi d'une donnée par un client et à quel leader

## Informations supplémentaires
Le projet est codé en python. Lorsque la commande `make` est lancée, les requirements sont installés.  
Version mpi4py : 3.1.1
  
Commandes du REPL:  
* `SPEED (low, medium, high) $PROCESS` : impacte la vitesse d’execution d’un processus
* `CRASH $PROCESS` : simule la mort d’un processus
* `START` : permet de dire aux client qu’ils peuvent, à partir de maintenant effectuer leurs demandes.
* `RECOVERY $PROCESS` : le processus $PROCESS précédemment crash revient à la vie 
* `END` : le programme se termine proprement (un message est envoyé à chaque processus)

## Auteurs
* Etienne Sharpin
* Laurélie Michielon
* Laura Lacambra
* Ségolène Denjoy
