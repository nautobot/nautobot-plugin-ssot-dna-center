# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!--next-version-placeholder-->

## v0.4.0 (2023-02-28)
### Feature
* ✨ Update CRUD methods for NautobotPort ([`2a34749`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/2a34749fde1d9eb6f1e2da7583a84756600ff0c5))
* ✨ Add enabled attribute to Port model ([`8a82c4c`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/8a82c4cb309f7661d417cad7f792e0ad9ed72452))
* ✨ Add load methods for each Port derived model. ([`410d285`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/410d285dcbb2ffe3e6a9f64dfdc2790e99cca0e4))
* ✨ Add method to get port information with device_id ([`0302bec`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/0302bec896474bdb9767326f67887459cfaf4851))
* ✨ Add initial Port derived classes for DNAC and Nautobot ([`b8b28a7`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/b8b28a74058bea95cd710b8f9cee742d073d6de0))
* ✨ Add Port base DiffSync model ([`dfe5b8c`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/dfe5b8c6e357240361b90a110aea6182618ddc34))

### Fix
* 🔥 Remove garbage characters in test_jobs ([`9a4b159`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/9a4b1598ad2af4ed8f8ab10b05e06c8589b0f834))
* 🐛 Ensure MAC address is string and formatted the same for diff ([`d01c28e`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/d01c28e076623786ccf0be39d9288e403722303e))
* 🐛 Ensure Location created with Site and Status and fix name. ([`363187d`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/363187d839d235759cef2c569b122fb14621a34f))
* 🐛 Add handling in case Device family attribute is null ([`41eeeda`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/41eeeda06670e770c31dfa3e752f8a198e2d154c))
* 🐛 Skip Devices without a hostname ([`1cd0308`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/1cd03086389722cc01d8456867b3c794b698189a))
* 🐛 Update DnacInstance class to derive from PrimaryModel ([`f362fae`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/f362fae92b64831448578a9760c541bd896063c7))

### Documentation
* 📝 Add informational logging to Nautobot CRUD methods. ([`5c63618`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/5c636182a1d2bb787a48356eb2a0fed2737b97b0))

## v0.3.1 (2023-02-17)
### Fix
* 🐛 Ensure version is recorded in Device CustomField ([`93b8282`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/93b82820579026422651077598b0133dab8017c7))

## v0.3.0 (2023-02-17)
### Feature
* Add Device import from DNAC #3 ([`9c8774e`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/9c8774eab9c2d08caef45f79e5a5341b91aa2927))
* Update Nautobot model CRUD methods ([`f76dfb6`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/f76dfb6dea16c47e9d2e875af0b6bf553bf5f427))
* ✨ Update NautobotDevice CRUD to use updated attributes. ([`cdeae35`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/cdeae350ee4f26850c16059491cac9eb2f31f647))
* ✨ Add load methods for devices from DNAC, include test to validate functionality. ([`ad40c25`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/ad40c25984f7628e512db0eec1548f2f7a028356))
* ✨ Add method to get_device_detail to get location data from DNAC ([`17114a5`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/17114a52d9d5c1cf2ca5a5b1d20212d6029921bd))
* ✨ Add method to find latitude and longitude from Device additionalInfo ([`3514834`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/3514834e7445807cc81bfd45224ea3a55072b3d9))

### Fix
* 🐛 Updates to ensure fields in diff line up and match ([`a659509`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/a659509468c6d5584a51309a61b4b04605ff4734))
* 🐛 Make parent an identifier to allow for nested areas ([`3831f25`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/3831f25417e58e93615f74162f9183ac580154a0))

### Documentation
* 📝 Update docstring for get_locations method ([`8c17deb`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/8c17deb2092e375b4acaabccbf294ffa74fed69e))

## v0.2.0 (2023-02-10)
### Feature
* Add Site load from DNAC and Nautobot ([#1](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/issues/1)) ([`0b42275`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/0b422757c614e067525b553a5520ef442a440f7e))
