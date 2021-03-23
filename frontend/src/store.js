import { proxy } from "valtio";

const subscriptions = proxy(
  JSON.parse(localStorage.getItem("subscriptions")) ?? {
    youtube: [],
    lbry: [],
    bitchute: [],
  }
);

export default subscriptions;
