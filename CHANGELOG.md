# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!--next-version-placeholder-->

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
