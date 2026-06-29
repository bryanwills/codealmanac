# Book repo

| Book | Code |
| ---- | ---- |
| [![Book Build Status](https://travis-ci.org/cosmicpython/book.svg?branch=master)](https://travis-ci.org/cosmicpython/book) | [![Code build status](https://travis-ci.org/cosmicpython/code.svg?branch=master)](https://travis-ci.org/cosmicpython/code) |


## Table of Contents

O'Reilly have generously said that we will be able to publish this book under a [CC license](LICENSE.md),
In the meantime, pull requests, typofixes, and more substantial feedback + suggestions are enthusiastically solicited.

| Chapter |       |
| ------- | ----- |
| [Preface](preface.md) | |
| [Introduction: Why do our designs go wrong?](introduction.md)| ||
| [**Part 1 Intro**](part1.md) | |
| [Chapter 1: Domain Model](chapter_01_domain_model.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_01_domain_model)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 2: Repository](chapter_02_repository.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_02_repository)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 3: Interlude: Abstractions](chapter_03_abstractions.md) | |
| [Chapter 4: Service Layer (and Flask API)](chapter_04_service_layer.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_04_service_layer)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 5: TDD in High Gear and Low Gear](chapter_05_high_gear_low_gear.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_05_high_gear_low_gear)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 6: Unit of Work](chapter_06_uow.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_06_uow)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 7: Aggregates](chapter_07_aggregate.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_07_aggregate)](https://travis-ci.org/cosmicpython/code) |
| [**Part 2 Intro**](part2.md) | |
| [Chapter 8: Domain Events and a Simple Message Bus](chapter_08_events_and_message_bus.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_08_events_and_message_bus)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 9: Going to Town on the MessageBus](chapter_09_all_messagebus.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_09_all_messagebus)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 10: Commands](chapter_10_commands.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_10_commands)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 11: External Events for Integration](chapter_11_external_events.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_11_external_events)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 12: CQRS](chapter_12_cqrs.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_12_cqrs)](https://travis-ci.org/cosmicpython/code) |
| [Chapter 13: Dependency Injection](chapter_13_dependency_injection.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=chapter_13_dependency_injection)](https://travis-ci.org/cosmicpython/code) |
| [Epilogue: How do I get there from here?](epilogue_1_how_to_get_there_from_here.md) | |
| [Appendix A: Recap table](appendix_ds1_table.md) | |
| [Appendix B: Project Structure](appendix_project_structure.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=appendix_project_structure)](https://travis-ci.org/cosmicpython/code) |
| [Appendix C: A major infrastructure change, made easy](appendix_csvs.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=appendix_csvs)](https://travis-ci.org/cosmicpython/code) |
| [Appendix D: Django](appendix_django.md) | [![Build Status](https://travis-ci.org/cosmicpython/code.svg?branch=appendix_django)](https://travis-ci.org/cosmicpython/code) |
| [Appendix F: Validation](appendix_validation.md) | |




Below is just instructions for me and bob really.

## Dependencies:

* asciidoctor
* Pygments (for syntax higlighting)
* asciidoctor-diagram (to render images from the text sources in [`./images`](./images))

```sh
gem install asciidoctor
python2 -m pip install --user pygments
gem install pygments.rb
gem install asciidoctor-diagram
```


## Commands

```sh
make html  # builds local .html versions of each chapter
make test  # does a sanity-check of the code listings
```
