# Conception et mise en œuvre de DiskMonitor, un moniteur temps réel des opérations de lecture et écriture sur un disque: cas de CentOS Stream

# Objectifs:

1. Comprendre le fonctionnement des E/S d’un  disque dur sous Linux.
2. Détecter les patterns d’accès disque : séquentiel, aléatoire, mixte.
3. Mesurer la latence, le débit, le blocage, la saturation des queues I/O.


# Fonctionnalités attendues
Créer un solution web permettant d’analyser et de visualiser les opérations sur disque en temps réel

# NB: README à mettre à jour progressivement par l'équipe.

Linux Disk Monitor

## Description

**Linux Disk Monitor** est une application de supervision permettant de surveiller l’utilisation des disques sur un système Linux.
Ce projet a été réalisé dans le cadre du Master 1 en Sécurité des Systèmes d’Information (SSI).

L’objectif principal est de fournir une solution simple, efficace et automatisée pour :


##  Fonctionnalités

* Analyse de l’espace disque disponible
* Affichage des partitions et de leur utilisation
* Détection des seuils critiques
* Interface simple (CLI ou Web selon ton projet)

##  Technologies utilisées

* Python 
* Linux (Centos stream)
* Bash scripting
* Git & GitHub
* html5
* css
* bootstrap
* java script

##  Installation

### 1. Cloner le projet

```bash
git clone https://github.com/OpenSecureFoundation/Linux-Disk-Monitor.git
cd Linux-Disk-Monitor
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate   # Linux
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## Utilisation

```bash
python main.py
```

---

## Exemple de sortie

```
Disk Usage:
------------------------
/dev/sda1 : 75% used
/dev/sda2 : 90% used 
```

---

##  Sécurité

Ce projet peut être intégré dans une stratégie de sécurité système pour :

* prévenir les attaques par saturation disque
* surveiller les anomalies système
* améliorer la disponibilité des services

---

## Contexte académique

Projet réalisé dans le cadre du Master 1 SSI, visant à appliquer les concepts de :

* supervision système
* administration Linux
* sécurité des infrastructures

---

##  Auteur

**Sylvain Ekosso**
Étudiant en Master SSI
Yaoundé, Cameroun 🇨🇲

---

## Licence

Ce projet est open-source et peut être utilisé à des fins éducatives et professionnelles.





Pour toute question ou collaboration, n’hésite pas à me contacter.
