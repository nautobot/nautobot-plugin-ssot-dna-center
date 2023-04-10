# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!--next-version-placeholder-->

## v0.7.0 (2023-04-10)
### Feature
* ✨ Add support for Device Lifecycle App for software version tracking. ([`65b4551`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/65b4551f74d4449f706ec17b939df2abe503d145))
* ✨ Create verify_platform function to get/create Platform to ensure standardized. ([`437770a`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/437770a2b53391cb951b0de0431c6ba8fba8306d))

### Fix
* 🐛 Remove metadata for py3.7 as not needed anymore ([`41d19f8`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/41d19f8d379912086062f49f9bde28fdb32816a8))

## v0.6.0 (2023-04-06)
### Feature
* ✨ Add CustomField to all imported devices stating SoR and last sync date/time. ([`1896b9c`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/1896b9c198b9d2ebd839bc73392c2c3089d5ee56))

### Fix
* 🐛 Correct CustomField name to match slug. This fixes the warning in Nautobot. ([`1dbe114`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/1dbe1143b1660d930673ac4737c49f8561d73f86))
* Add handling in case a Site has no Region. ([`ce4dd97`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/ce4dd977a376bd061a81c6d5790fe1ce450d5af6))

## v0.5.0 (2023-04-04)
### Feature
* ✨ Add tenant to supported models ([`b1fa72c`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/b1fa72c7f832d39d77b6f6a16a6ee05d96ceb080))
* ✨ Add Tenant to DNACInstance model ([`ca70638`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/ca70638e8d24cb2b1c1b1b84206925be91837cf3))
* ✨ Add DNA Center logo and update data mappings for IP Addresses ([`1cb2f19`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/1cb2f19a014eec7f58a8d1e9aad8fd0df71ecd20))
* ✨ Add sync_complete method to process deletion of location objects ([`0a0990c`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/0a0990cbbb4f0b6940ffc1c00bee733a15e2d085))
* ✨ Add validation to DNACInstance model and update tests accordingly ([`5512b0a`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/5512b0a81219cfbc62b92a18395d83be1f31bd2f))
* ✨ Add IPAddresses from Interfaces to imports and CRUD ops to Nautobot. ([`6dc9181`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/6dc9181884bfa4a4d905dc5d584c28ceb3bb2e2c))

### Fix
* 🐛 Add Tenant to forms to enable specifying in DNACInstance. ([`354644f`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/354644f9d5a1709277c4bcc74e466c161c277abe))
* Correct slug for OS Version CF to be a dash ([`f998470`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/f99847017688096c030bb8d233f4f020b5396a31))
* Add update_forward_ref to all parent models ([`78c161e`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/78c161e8d8b5a744b4a6f36d4acff90725ae5907))
* 🐛 Make management_addr attribute optional as it's not being evaluated in attribute list ([`9c43390`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/9c433907bce0e4c59209770100413063f5fa4963))

### Documentation
* 📝 Add docstring to test_delete method ([`31abd51`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/31abd51a0254dd58d6b5ddebac0900b28f95d2a6))

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
