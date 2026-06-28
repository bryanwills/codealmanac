import { Command } from "commander";

import { registerTopicCreateCommand } from "./register-topic-create-command.js";
import { registerTopicEdgeCommands } from "./register-topic-edge-commands.js";
import { registerTopicMutationCommands } from "./register-topic-mutation-commands.js";
import { registerTopicReadCommands } from "./register-topic-read-commands.js";

export function registerTopicsCommands(program: Command): void {
  const topics = program
    .command("topics")
    .description("manage the topic DAG");

  registerTopicReadCommands(topics);
  registerTopicCreateCommand(topics);
  registerTopicEdgeCommands(topics);
  registerTopicMutationCommands(topics);
}
