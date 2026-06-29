<!-- Generated mechanically from Architecture Patterns with Python AsciiDoc source. -->
<!-- Source file: appendix_ds1_table.asciidoc. Do not edit book text here; regenerate from upstream if needed. -->

## Summary Diagram and Table

Here's what our architecture looks like by the end of the book:

![images/apwp_aa01.png](images/apwp_aa01.png)

ds1_table recaps each pattern and what it does.

.The components of our architecture and what they all do
[cols="1,1,2"]

| Layer | Component | Description

.5+a| *Domain*

__Defines the business logic.__


| Entity | A domain object whose attributes may change but that has a recognizable identity over time.

| Value object | An immutable domain object whose attributes entirely define it. It is fungible with other identical objects.

| Aggregate | Cluster of associated objects that we treat as a unit for the purpose of data changes. Defines and enforces a consistency boundary.

| Event | Represents something that happened.

| Command | Represents a job the system should perform.

.3+a| *Service Layer*

__Defines the jobs the system should perform and orchestrates different components.__

| Handler | Receives a command or an event and performs what needs to happen.
| Unit of work | Abstraction around data integrity. Each unit of work represents an atomic update. Makes repositories available. Tracks new events on retrieved aggregates.
| Message bus (internal) | Handles commands and events by routing them to the appropriate handler.

.2+a| *Adapters* (Secondary)

__Concrete implementations of an interface that goes from our system
to the outside world (I/O).__

| Repository | Abstraction around persistent storage. Each aggregate has its own repository.
| Event publisher | Pushes events onto the external message bus.

.2+a| *Entrypoints* (Primary adapters)

__Translate external inputs into calls into the service layer.__

| Web | Receives web requests and translates them into commands, passing them to the internal message bus.
| Event consumer | Reads events from the external message bus and translates them into commands, passing them to the internal message bus.

| N/A | External message bus (message broker) | A piece of infrastructure that different services use to intercommunicate, via events.
