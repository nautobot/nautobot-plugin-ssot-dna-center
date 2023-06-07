# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!--next-version-placeholder-->

## v1.0.0 (2023-06-07)
### Feature
* ✨ Update Device load function to hostname_mapping setting is found. ([`8ecdd8b`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/8ecdd8bbf1e1ff1b0b2dd7aa252f7371e377114b))
* ✨ Add new function to parse hostname to determine DeviceRole. ([`91b139f`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/91b139f51b0fd1c4460777c798058dc86201619d))

### Documentation
* 📝 Update README with details about hostname_mapping and other settings. ([`17b02a1`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/17b02a122e7d07a9e733842a5d2ae24753c95ee6))

## v0.9.0 (2023-05-22)
### Feature
* Add failed_import_devices list for field validation. ([`55ace49`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/55ace49c25cc9e81dba2b02b57de7ceae475cc8e))

### Fix
* :bug: Correct updates for role and device type as they're tuples ([`bd69d61`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/bd69d6124a204f30dc4a3ed103389adb085b808f))
* :bug: Correct attribute to facility from site ([`c6e2294`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/c6e2294e9a09cb338adb8d3898dcf719654ef5ed))
* :bug: Only do DLC check if version in attrs for update ([`cef860d`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/cef860d359e094c5538422b37c4b17283d7b6e02))
* :bug: Remove filter using DNAC CF on Floor ([`379eba8`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/379eba81f0644c0aec671aa3e5805656b0c760f4))
* Remove management_addr from _attributes on Device ([`6037ddc`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/6037ddc634545c7ab8c752d41323b9dff75f8170))
* Correct Sync CF to just be date ([`15b30ed`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/15b30ed56499b00bb274477fbefaae565fb9a6d1))
* Correct query for Device when loading ports ([`e788adb`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/e788adb3f4f0b29962dd8694024b374dec5f1b33))

## v0.8.0 (2023-04-26)
### Feature
* ✨ Update Job to execute sync in post_run to make it non-atomic. ([`20579ff`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/20579ff084017bb266e0a6dee2e804307c05df8a))
* ✨ Add update_locations setting to disable updating/deleting of Sites from DNAC ([`bb6c8cb`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/bb6c8cba4a48a4491dd21e3111bd3b093d2dd6c4))
* ✨ Add setting to ignore Global Area so it's not imported. ([`1a31745`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/1a31745d5f510ce48f7dd5bdcd9738b08608bc89))

### Fix
* 🐛 Ensure serial on Device is always a string, can't be None in Nautobot. ([`09fc158`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/09fc1587df421dc740ac611e4268a0171a4ea626))
* 🐛 Add check for already loaded Building in case of duplicates in DNAC. ([`2227653`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/22276534e7bcdbb4dc8617840030d5bc300d574b))
* 🐛 Specify Interface when finding IPAddress to update CustomFields. ([`82caba6`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/82caba64b7e88f6e580163abc45100374f64b70f))
* 🐛 Add Tenant field to tables ([`aed644a`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/aed644a345206c73a15bca960874f9e2460e0009))
* Use is_truthy with import_global setting ([`44a2fd0`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/44a2fd07401e174217cdd442c3571e34c8ef4489))
* ♻️ Redo code to work properly without Global area. Also added tests to validate functionality. ([`3f70ada`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/3f70ada8d87ee2b3c49682cd85fce7e27ee597c5))
* 🐛 Add check for existing Region in create function. ([`0908b5e`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/0908b5ee19d396bef8c9ba1ec7471451952dc9c3))
* 🐛 Add check for type value being non-null ([`1d360be`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/1d360be4842c1c2bd346062f0e79fbcb0b24b5c5))
* 🐛 Add check for existing Port before loading to avoid duplicates. ([`be4d386`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/be4d386140d2471e8c51111624d9aee23dfdde6a))
* Add handling for validating device already loaded to prevent possible duplicates. ([`690cd93`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/690cd933dcd917db2c8c1c5e35f8b682118968d6))
* 🐛 Add check for MTU being null, set to 1500 if found. ([`6c2946f`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/6c2946f022d313749ce3e6dd9e01b1655c6e50bd))
* Have model set to Unknown if null in DNAC ([`a0c2f65`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/a0c2f65f2146bf8118cf857d69b728b61499ac23))
* 🐛 Update get_devices to be less than, ensure offset has minimum of 1. ([`983d96e`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/983d96e1a1cfdd92f3e8ed2f25ca9879bd0d1c34))
* 🐛 Update get_locations to remove duplicate results and add pagination handling. ([`c0a6c19`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/c0a6c19e747fcb8d6b7ff9bda2896fc8ca8c258c))
* 🐛 Add handling for more than 500 responses for getting sites and devices. ([`440342f`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/440342f8a19d89151aad695f74a744959e2e3649))

### Documentation
* 📝 Update documentation with import_global setting ([`0e6c53d`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/0e6c53d3cb4ffcfbe6ccb1d2839511f137d75892))
* 📝 Add logging to notify user of errors. ([`4b0e8fa`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/4b0e8fa9aed9822465f685f5c3b944bbcb5c5c3a))
* 📝 Add some debug logging to DNAC load functions ([`343c22c`](https://github.com/networktocode-llc/nautobot-plugin-ssot-dna-center/commit/343c22c44b7841c8c7d9f89f6319f711ff7582b9))

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
