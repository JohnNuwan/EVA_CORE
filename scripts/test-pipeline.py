#!/usr/bin/env python3
"""Module de test pour valider le pipeline critic → cicd → commit auto."""
import sys
import json  # noqa: unused — sera détecté par le critic
import time
import re  # noqa: unused — sera détecté par le critic


def process_data(data):
    """Traite les données."""
    # TODO: implémenter le traitement
    result = data * 2
    return result


if __name__ == "__main__":
    print(process_data(42))
