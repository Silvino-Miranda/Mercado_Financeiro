"""
Teste de imports v3 (sem TensorFlow)
"""
import time

print("="*80)
print("TESTE DE IMPORTS V3 (SEM TENSORFLOW)")
print("="*80)

# 1. Pandas/NumPy
print("\n1️⃣ Testando Pandas/NumPy...")
start = time.time()
import pandas as pd
import numpy as np
print(f"   ✅ OK ({time.time()-start:.2f}s)")

# 2. Scikit-learn
print("\n2️⃣ Testando Scikit-learn...")
start = time.time()
from sklearn.preprocessing import StandardScaler
print(f"   ✅ OK ({time.time()-start:.2f}s)")

# 3. TensorFlow (pode demorar)
print("\n3️⃣ Testando TensorFlow (AGUARDE ~15 segundos)...")
start = time.time()
import tensorflow as tf
print(f"   ✅ OK ({time.time()-start:.2f}s)")
print(f"   📦 TensorFlow version: {tf.__version__}")

# 4. Keras
print("\n4️⃣ Testando Keras...")
start = time.time()
from tensorflow import keras
print(f"   ✅ OK ({time.time()-start:.2f}s)")

print("\n" + "="*80)
print("✅ TODOS OS IMPORTS FUNCIONARAM!")
print("="*80)
print("\n💡 AGORA VOCÊ PODE EXECUTAR O TREINAMENTO V3!")
