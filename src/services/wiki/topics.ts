export {
  listWikiTopics,
  readWikiTopic,
} from "./topic-read.js";
export {
  createWikiTopic,
  deleteWikiTopic,
  describeWikiTopic,
  linkWikiTopics,
  renameWikiTopic,
  unlinkWikiTopics,
} from "./topic-mutations.js";
export type {
  CreateWikiTopicRequest,
  CreateWikiTopicResult,
  DeleteWikiTopicRequest,
  DeleteWikiTopicResult,
  DescribeWikiTopicRequest,
  DescribeWikiTopicResult,
  LinkWikiTopicsRequest,
  LinkWikiTopicsResult,
  RenameWikiTopicRequest,
  RenameWikiTopicResult,
  UnlinkWikiTopicsRequest,
  UnlinkWikiTopicsResult,
  WikiTopicRecord,
  WikiTopicRequest,
  WikiTopicResult,
  WikiTopicSummary,
  WikiTopicsRequest,
} from "./topic-types.js";
