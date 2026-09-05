# Two-Way Digital Paging System Using BladeRF SDRs

![SDR](https://img.shields.io/badge/Hardware-BladeRF_SDR-blue?style=for-the-badge)
![DSP](https://img.shields.io/badge/Software-GNU_Radio-orange?style=for-the-badge)
![Telecom](https://img.shields.io/badge/Domain-Digital_Communications-success?style=for-the-badge)

*A robust two-way digital communication testbed bridging theoretical signal processing with physical Software Defined Radio (SDR) hardware implementation.*

<p align="center">
  <img src="images/Frame Structure.png" width="70%" />
</p>

---

## 📋 Project Overview
This project focuses on the design and realization of a functional two-way digital paging system. Utilizing BladeRF Software Defined Radios (SDRs), the system establishes a reliable over-the-air digital communication link, translating mathematical digital signal processing (DSP) concepts into a physical transmission pipeline. 

---

## ⚙️ Core System Architecture & Logic
The software architecture dictates the complete lifecycle of the digital paging data over the RF link. My primary contribution focused on engineering the core process logic, which includes:

*   **Digital Modulation & Demodulation:** Architecting the signal processing pipeline to accurately map digital payloads onto the RF carrier and extract them at the receiver.
*   **Frame Synchronization:** Implementing robust synchronization mechanisms to ensure the receiver correctly aligns with incoming packet boundaries despite over-the-air channel delays and phase shifts.
*   **Two-Way Acknowledgement Protocol:** Designing the handshake and acknowledgment (ACK) logic to verify successful packet delivery, ensuring a reliable, bi-directional communication loop.
*   **Data Pipeline Integration:** Managing the flow of data through discrete DSP blocks to maintain signal integrity between the physical SDR hardware and the software layer.

---

## 🛠️ Technology Stack
*   **Hardware:** BladeRF Software Defined Radios (SDR)
*   **Software Framework:** GNU Radio / Digital Signal Processing algorithms
*   **Domain:** RF Engineering, Telecommunication Networks, Digital Communications

---

## 🤝 The Engineering Team
This communication testbed was engineered by undergraduates at the Department of Electronic and Telecommunication Engineering, University of Moratuwa:
*   **Pramod Aroshana**
*   **[Hasindu Wanigasundara]**
*   **[Deelaka de Mel]**
*   **[Rakesh Ratheeshan]**
