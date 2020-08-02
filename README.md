# wireguard-generator

## What does it do?
This is an app designed to be deployed as a wireguard manager. It will generate new configs for peers to connect, and authorise them via the wg binary. 
**Quick pro tip**: wg binary has to have net_admin capability to avoid running as root

## Why does it exist?
Being in control of the binary allows us to create a makeshift VPN and allow users to generate a config and connect, while keeping intruders away. This is useful when you want a handful of people to be able to *automatically* generate configs for themselves and connect to the VPS. My use case was a school CTF where contesters were able to connect to the machines.

**Note:** This application only assigns ip addresses and generates new configs. Wireguard on the server requires setting up, espetially if you intend to use it as a router.
