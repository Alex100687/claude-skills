# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, 'My_Knowledge_Base/Scripts')
import cover_gen
cover_gen.OUTPUT_PATH = os.path.join('My_Knowledge_Base', 'Cover_Elements', 'output', 'cover.png')
os.makedirs(os.path.dirname(cover_gen.OUTPUT_PATH), exist_ok=True)
cover_gen.generate_cover()
print("Cover generated: " + cover_gen.OUTPUT_PATH)
