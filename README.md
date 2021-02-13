<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/mark483/multithreading-for-websocket">
    <img src="kite.png" width="80" height="80">
  </a>

  <h1 align="center">kite-multithreading-for-websocket</h3>

  <p align="center">
    A multi-threaded kite client using websocket connection
    <br />
    ·
    <a href="https://github.com/mark483/multithreading-for-websocket/issues">Report Bug</a>
    ·
    <a href="https://github.com/mark483/multithreading-for-websocket/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This is a python client for kite trade using a set of REST-like APIs that expose many capabilities required to build a complete investment and trading platform. Execute orders in real time, stream live market data (WebSockets), and more.

The project retrieves a list of 3000 instrument tokens which is the maximum allowed for a single connection.

The client starts receiving ticks on the main thread which inserts them in a queue for worker threads to fetch from.

Worker threads fetch responses from global queue and start performing analysis.

The output is a list of top 10 traded stocks sorted by traded_price rocp and traded_value average.

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* python 3.6+
  ```sh
  https://www.python.org/downloads/
  ```
* Environment Variables

You need to provide your own .env file in the root directory that contains your Kite credentials such as KITE_API_KEY,KITE_API_SECRET_KEY ,etc...

*Flask model

You need to provide a flask model to run your server,note that currently server runs on localhost

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/mark483/multithreading-for-websocket.git
   ```
2. Install python packages
   ```sh
   pip install -r requirements.txt
   ```


<!-- USAGE EXAMPLES -->
## Usage
1. run flask server
   ```sh
   python app.py
   ```
2. Run client
   ```sh
   python kite_wbsk_mom.py
   ```



<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/mark483/multithreading-for-websocket/issues) for a list of proposed features (and known issues).



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

Distributed under the MIT License. See `LICENSE` for more information.





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/mark483/kite-multithreading-for-websocket.svg?style=for-the-badge
[contributors-url]: https://github.com/mark483/kite-multithreading-for-websocket/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/mark483/kite-multithreading-for-websocket.svg?style=for-the-badge
[forks-url]: https://github.com/mark483/kite-multithreading-for-websocket/network/members
[stars-shield]: https://img.shields.io/github/stars/mark483/kite-multithreading-for-websocket.svg?style=for-the-badge
[stars-url]: https://github.com/mark483/kite-multithreading-for-websocket/stargazers
[issues-shield]: https://img.shields.io/github/issues/mark483/kite-multithreading-for-websocket.svg?style=for-the-badge
[issues-url]: https://github.com/mark483/kite-multithreading-for-websocket/issues
[license-shield]: https://img.shields.io/github/license/mark483/kite-multithreading-for-websocket.svg?style=for-the-badge
[license-url]: https://github.com/mark483/kite-multithreading-for-websocket/blob/main/LICENSE
