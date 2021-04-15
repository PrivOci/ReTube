import { proxy } from "valtio";

const subscriptions = proxy(
  JSON.parse(localStorage.getItem("subscriptions")) ?? {
    youtube: [],
    lbry: [],
    bitchute: [],
    config: {
      "spell_checker": false,
    },
  }
);

export default subscriptions;
