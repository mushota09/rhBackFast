#!/usr/bin/env python3
import sys

# Read the template from stdin or a file
lines = [
    '"""Services de logique métier pour la gestion des congés"""',
    'from datetime import date, datetime',
    'from typing import List, Optional, Tuple',
    'from sqlalchemy import select',
    'from sqlalchemy.ext.asyncio import AsyncSession',
    'import holidays',
    '',
    'from app.conge_app.models import (',
    '    JourFerie, SoldeConge, DemandeConge, TypeConge, HistoriqueConge',
    ')',
    'from app.conge_app.utils import (',
    '    is_weekend,',
    '    count_w
