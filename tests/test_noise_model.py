import math
import random


import c2qa
import numpy as np
import qiskit


def test_noise_model(capsys):
    with capsys.disabled():
        num_qumodes = 1
        num_qubits_per_qumode = 2
        qmr = c2qa.QumodeRegister(num_qumodes, num_qubits_per_qumode)
        qr = qiskit.QuantumRegister(2)
        circuit = c2qa.CVCircuit(qmr, qr)

        for qumode in range(num_qumodes):
            circuit.cv_initialize(0, qmr[qumode])

        circuit.initialize([0, 1], qr[1])  # qr[0] will init to zero

        alpha = random.random()
        beta = random.random()
        circuit.cv_cnd_d(alpha, -beta, qr[0], qmr[0])
        circuit.cv_cnd_d(-alpha, beta, qr[0], qmr[0])

        circuit.cv_cnd_d(alpha, -beta, qr[1], qmr[0])
        circuit.cv_cnd_d(-alpha, beta, qr[1], qmr[0])

        # prob = 0.01
        # kraus = circuit.ops.a * circuit.ops.a_dag
        # kraus_operators = [circuit.ops.a.toarray().tolist(), circuit.ops.a_dag.toarray().tolist()]

        # theta = np.pi / 2
        # kraus_operators = [[[1, 0],[0, math.sin(theta)]], [[0, math.cos(theta)],[0, 0]]]

        num_photons = circuit.cutoff
        photon_loss_rate = 0.01
        time = 10.0
        kraus_operators = c2qa.kraus.calculate_kraus(num_photons, photon_loss_rate, time, circuit.ops.a, circuit.ops.a_dag)

        print("kraus")
        print(kraus_operators)

        state, result = c2qa.util.simulate(circuit, kraus_operators=kraus_operators)


def test_kraus_operators(capsys):
    with capsys.disabled():
        num_qumodes = 1
        num_qubits_per_qumode = 2
        qmr = c2qa.QumodeRegister(num_qumodes, num_qubits_per_qumode)
        qr = qiskit.QuantumRegister(2)
        circuit = c2qa.CVCircuit(qmr, qr)
        
        num_photons = circuit.cutoff
        photon_loss_rate = 0.01
        time = 10.0
        kraus_operators = c2qa.kraus.calculate_kraus(num_photons, photon_loss_rate, time, circuit.ops.a, circuit.ops.a_dag)
        print()
        print("Kraus Operators")
        for op in kraus_operators:
            print(op)

        kraus = qiskit.quantum_info.operators.channel.Kraus(kraus_operators)        
        assert kraus.is_cp(), "Is not completely positive"

        accum = 0j
        for op in kraus_operators:
            accum += np.dot(np.transpose(np.conj(op)), op)

        print("Sum")
        print(accum)

        is_identity = (accum.shape[0] == accum.shape[1]) and np.allclose(accum, np.eye(accum.shape[0]))
        assert is_identity, "Sum is not identity"

        assert kraus.is_tp(), "Is not trace preserving"
        assert kraus.is_cptp(), "Is not CPTP"
