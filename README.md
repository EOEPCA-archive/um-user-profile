<!--
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** um-user-profile
-->

<!-- PROJECT SHIELDS -->
<!--
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
![Build][build-shield]

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/EOEPCA/um-user-profile">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">um-user-profile</h3>

  <p align="center">
    EOEPCA's User profile
    <br />
    <a href="https://eoepca.github.io/um-user-profile/"><strong>Explore the docs »</strong></a>
    <br />
    <a href="https://github.com/EOEPCA/um-user-profile/issues">Report Bug</a>
    ·
    <a href="https://github.com/EOEPCA/um-user-profile/issues">Request Feature</a>
  </p>
</p>

## Table of Contents

- [Table of Contents](#table-of-contents)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

<!-- ABOUT THE PROJECT -->

### Built With

- [Python](https://www.python.org//)
- [PyTest](https://docs.pytest.org)
- [YAML](https://yaml.org/)
- [Travis CI](https://travis-ci.com/)

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.

- [Docker](https://www.docker.com/)
- [Python](https://www.python.org//)

### Installation

1. Get into EOEPCA's development environment

```sh
vagrant ssh
```

3. Clone the repo

```sh
git clone https://github.com/EOEPCA/um-user-profile.git
```

4. Change local directory

```sh
cd template-service
```

## Configuration

The User Profile building block gets all its configuration from the file located under `src/config/WEB_config.json`.
The parameters that are accepted, and their meaning, are as follows:
- **sso_url**: hostname or IP of the Auth Server.
- **title**: Title that will be seen when navigating to the web interface
- **scopes**: Scopes used for the internal OAUTH client. Currently, the required are: "openid", "email" and "user_name"
- **client_id**: Client ID used for the internal OAUTH client.
- **client_secret**: Client secret for the corresponding client_id.
- **redirect_uri**: Redirect URI configured in the client, which should point to this service's callback URL.
- **post_logout_redirect_uri**: Redirect URI for post logout of a user.
- **base_uri**: Base URI for all requests against the web server
- **oauth_callback_path**: Callback path for the end of a succesful oauth flow.
- **logout_endpoint**: Endpoint for the logout of a currently logged in user.
- **service_host**: Host to listen on (localhost, 0.0.0.0, etc..)
- **service_port**: Port to listen on for the web server
- **protected_attributes**: Attributes that the user can see about their profiles, but not edit
- **blacklist_attributes**: Attributes that the user can not see or edit.
- **separator_ui_attributes**: Separator used for multi-level attributes
- **color_web_background**: Color used for the background of the web, in HEX.
- **color_web_header**: Color used for the header of the web, in HEX.
- **logo_alt_name**: Alternative name for logo of the web
- **logo_image_path**: Path to logo of the web
- **color_header_table**: Color used for the header of any table
- **color_text_header_table**: Color used for the content of any table
- **color_button_modify**: Color used for the modify button
- **use_threads**: Toggle threads for requests. Enabling this in production is recommended
- **debug_mode**: Toggle debug mode, which enables a debug web interface, more errors and logs.

## Documentation

The component documentation can be found at https://eoepca.github.io/um-user-profile/.

<!-- ROADMAP -->

## Roadmap

See the [open issues](https://github.com/EOEPCA/um-user-profile/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->

## License

Distributed under the Apache-2.0 License. See `LICENSE` for more information.

## Contact

EOEPCA mailbox - eoepca.systemteam@telespazio.com

Project Link: [https://github.com/EOEPCA/um-user-profile](https://github.com/EOEPCA/um-user-profile)

## Acknowledgements

- README.md is based on [this template](https://github.com/othneildrew/Best-README-Template) by [Othneil Drew](https://github.com/othneildrew).


[contributors-shield]: https://img.shields.io/github/contributors/EOEPCA/um-user-profile.svg?style=flat-square
[contributors-url]: https://github.com/EOEPCA/um-user-profile/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/EOEPCA/um-user-profile.svg?style=flat-square
[forks-url]: https://github.com/EOEPCA/um-user-profile/network/members
[stars-shield]: https://img.shields.io/github/stars/EOEPCA/um-user-profile.svg?style=flat-square
[stars-url]: https://github.com/EOEPCA/um-user-profile/stargazers
[issues-shield]: https://img.shields.io/github/issues/EOEPCA/um-user-profile.svg?style=flat-square
[issues-url]: https://github.com/EOEPCA/um-user-profile/issues
[license-shield]: https://img.shields.io/github/license/EOEPCA/um-user-profile.svg?style=flat-square
[license-url]: https://github.com/EOEPCA/um-user-profile/blob/master/LICENSE
[build-shield]: https://www.travis-ci.com/EOEPCA/um-user-profile.svg?branch=master
