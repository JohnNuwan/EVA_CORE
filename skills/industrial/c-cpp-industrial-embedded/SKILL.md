---
name: c-cpp-industrial-embedded
description: "Programmer en C et C++ pour l'embarqué et le temps réel."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, windows]
metadata:
  tags: [c, cpp, embedded, realtime, plcnext, twincat, ethercat, profinet, fieldbus, cross-compilation]
  related_skills: [iec61131-3-programming-standards, rust-cython-for-industry, ot-it-integration-languages]
---

# Programmation C / C++ Temps Réel et Systèmes Industriels Embarqués

Cette compétence encadre le développement d'applications bas niveau en C et C++ destinées aux microcontrôleurs, aux ordinateurs industriels durcis (IPC), aux automates programmables ouverts (PLCnext, TwinCAT) et aux bus de terrain temps réel.

---

## 1. Programmation Temps Réel Déterministe sous Linux RT-PREEMPT

Pour garantir qu'une tâche s'exécute précisément à intervalles réguliers (gigue inférieure à quelques microsecondes), il est indispensable d'utiliser l'ordonnanceur temps réel et de verrouiller l'espace mémoire.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sched.h>
#include <sys/mman.h>
#include <pthread.h>

#define NANO_SECONDS_PER_SEC 1000000000

// Fonction exécutée par le thread temps réel
void* rt_periodic_task(void* arg) {
    struct sched_param param;
    param.sched_priority = 99; // Priorité temps réel max sous Linux

    // Définition de la politique d'ordonnancement FIFO temps réel
    if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &param) == -1) {
        perror("pthread_setschedparam a échoué");
        return NULL;
    }

    // Verrouillage de la mémoire virtuelle pour éviter les défauts de page (page faults)
    if (mlockall(MCL_CURRENT | MCL_FUTURE) == -1) {
        perror("mlockall a échoué");
        return NULL;
    }

    struct timespec next_period;
    clock_gettime(CLOCK_MONOTONIC, &next_period);

    long period_ns = 1000000; // Période de 1 milliseconde (1 000 000 ns)

    while (1) {
        // Calcul du prochain point de réveil
        next_period.tv_nsec += period_ns;
        while (next_period.tv_nsec >= NANO_SECONDS_PER_SEC) {
            next_period.tv_nsec -= NANO_SECONDS_PER_SEC;
            next_period.tv_sec++;
        }

        // Sommeil de précision jusqu'à l'échéance calculée
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_period, NULL);

        // --- TRAITEMENT TEMPS RÉEL (Contrôle, Acquisition de capteurs) ---
        // Pas d'allocation mémoire (malloc, std::vector) ni d'I/O bloquante (printf) ici
    }
    return NULL;
}
```

---

## 2. Intégration C++ sur Automates de Nouvelle Génération

### Phoenix Contact PLCnext (Exemple de Component C++)
Les composants C++ PLCnext s'interfacent avec le Global Data Space (GDS).

```cpp
#include "Arp/System/Core/Arp.h"
#include "Arp/System/Commons/Logging.h"
#include "Arp/Plc/Commons/Domain/ComponentBase.h"

namespace Actemium {

class MainPlcComponent : public Arp::Plc::Commons::Domain::ComponentBase
{
public:
    MainPlcComponent(IApplication& application, const String& name);
    virtual ~MainPlcComponent() = default;

    void Initialize() override;
    void LoadConfig() override;
    void SetupConfig() override;
    void ResetConfig() override;

    // Déclaration des ports d'E/S mappés dans le GDS
    //#port
    //#attributes(Input)
    int32 input_laser_distance_mm = 0;

    //#port
    //#attributes(Output)
    bool output_ejection_cylinder = false;

    // Méthode appelée cycliquement par le gestionnaire d'exécution
    void ExecuteCyclic()
    {
        // Logique de tri ultra-rapide
        if (input_laser_distance_mm > 150) {
            output_ejection_cylinder = true;
        } else {
            output_ejection_cylinder = false;
        }
    }
};

} // namespace Actemium
```

---

## 3. Communication de Bus de Terrain Directe (SocketCAN)

CANopen et DeviceNet s'appuient sur le bus physique CAN. Sous Linux, SocketCAN permet de manipuler les trames comme des connexions réseau.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>

int init_can_port(const char* interface_name) {
    int s;
    struct sockaddr_can addr;
    struct ifreq ifr;

    // Création d'un socket CAN brut
    if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
        perror("Erreur création socket CAN");
        return -1;
    }

    strcpy(ifr.ifr_name, interface_name);
    ioctl(s, SIOCGIFINDEX, &ifr); // Résolution de l'index de l'interface (ex: can0)

    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Erreur association socket CAN");
        close(s);
        return -1;
    }
    return s;
}

int send_motor_torque_command(int socket_fd, uint16_t node_id, int16_t torque_value) {
    struct can_frame frame;
    
    // Identifiant CAN : 0x200 (RPDO1) + Node ID
    frame.can_id = 0x200 + node_id;
    frame.can_dlc = 2; // Commande sur 2 octets (int16)
    
    // Remplissage binaire en Big-Endian
    frame.data[0] = (torque_value >> 8) & 0xFF;
    frame.data[1] = torque_value & 0xFF;

    if (write(socket_fd, &frame, sizeof(struct can_frame)) != sizeof(struct can_frame)) {
        perror("Échec envoi trame CAN");
        return -1;
    }
    return 0;
}
```

---

## 4. Règles de Sécurité Mémoire et Temps Réel (C++)

* **Pas de STL dynamique en boucle cyclique** : N'utilisez pas `std::vector::push_back`, `std::string` ou `std::shared_ptr` dans la boucle temps réel car ils provoquent des allocations mémoire dynamiques invisibles sous le capot. Utilisez `std::array` ou pré-allouez la capacité des vecteurs au démarrage (`std::vector::reserve`).
* **Gestion du tas (Heap)** : Instanciez tous vos objets au démarrage dans la phase d'initialisation de l'automate. Les destructeurs ne doivent pas non plus être appelés en boucle cyclique.
* **Diagnostics statiques** : Utilisez l'analyse statique (`cppcheck`, `clang-tidy`) et compilez avec `-Wall -Wextra -Werror` pour interdire tout comportement indéterminé du compilateur.
