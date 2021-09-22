import React, { useState } from "react";
import BoxForContent from "./BoxForContent";
import Link from "next/link";
import { subscriptions } from "./data";
import { useSnapshot } from "valtio";
import { useToasts } from "react-toast-notifications";
import _ from "lodash";

const Settings = () => {
  const subsReadOnly = useSnapshot(subscriptions);

  // file upload - YouTube
  const [selectedFileYT, setSelectedFileYT] = useState();
  const [isFilePickedYT, setIsFilePickedYT] = useState(false);

  const changeHandlerYouTube = (event) => {
    setSelectedFileYT(event.target.files.item(0));
    setIsFilePickedYT(true);
  };

  const { addToast } = useToasts();
  const handleSubmissionYouTube = async () => {
    console.log(selectedFileYT);
    const fileContent = await selectedFileYT.text();
    const jsonContent = JSON.parse(fileContent);
    // prepare list
    jsonContent.forEach((element) => {
      subscriptions.youtube.push(element["snippet"]["resourceId"]["channelId"]);
    });
    subscriptions.youtube = [...new Set(subscriptions.youtube)];
    localStorage.setItem("subscriptions", JSON.stringify(subscriptions));
    addToast("YouTube subscriptions updated", {
      appearance: "success",
      autoDismiss: true,
    });
    setIsFilePickedYT(false);
  };

  // file upload ReTube
  const [selectedFileRT, setSelectedFileRT] = useState();
  const [isFilePickedRT, setIsFilePickedRT] = useState(false);

  const changeHandlerRT = (event) => {
    setSelectedFileRT(event.target.files.item(0));
    setIsFilePickedRT(true);
  };

  const handleSubmissionRT = async () => {
    console.log(selectedFileRT);
    const fileContent = await selectedFileRT.text();

    const jsonContent = JSON.parse(fileContent);
    const ytJson = jsonContent["youtube"];
    const bcJson = jsonContent["bitchute"];
    const lbJson = jsonContent["lbry"];

    subscriptions.youtube = _.merge(subscriptions.youtube, ytJson);
    subscriptions.bitchute = _.merge(subscriptions.bitchute, bcJson);
    subscriptions.lbry = _.merge(subscriptions.lbry, lbJson);

    localStorage.setItem("subscriptions", JSON.stringify(subscriptions));
    addToast("ReTube subscriptions updated", {
      appearance: "success",
      autoDismiss: true,
    });

    setIsFilePickedRT(false);
  };

  // file upload Bitchute
  const [selectedFileBT, setSelectedFileBT] = useState();
  const [isFilePickedBT, setIsFilePickedBT] = useState(false);

  const changeHandlerBT = (event) => {
    setSelectedFileBT(event.target.files.item(0));
    setIsFilePickedBT(true);
  };

  const handleSubmissionBT = async () => {
    console.log(selectedFileBT);
    // https://www.bitchute.com/subscriptions/
    const fileContent = await selectedFileBT.text();

    const parser = new DOMParser();
    const htmlDoc = parser.parseFromString(fileContent, "text/html");
    const subsBox = htmlDoc.getElementById("page-detail");
    const subsBoxList = subsBox.getElementsByClassName(
      "subscription-container"
    );
    [...subsBoxList].forEach((element) => {
      // /channel/channelId/ => channelId
      let channelId = element.getElementsByTagName("a")[0].getAttribute("href");
      channelId = channelId.split("channel/")[1].slice(0, -1);
      subscriptions.bitchute.push(channelId);
    });

    subscriptions.bitchute = [...new Set(subscriptions.bitchute)];
    localStorage.setItem("subscriptions", JSON.stringify(subscriptions));
    addToast("Bitchute subscriptions updated", {
      appearance: "success",
      autoDismiss: true,
    });
    setIsFilePickedLbry(false);
  };

  return (
    <div className="grid gap-4 mt-4">
      <BoxForContent>
        <div>
          <Link href="https://github.com/iv-org/documentation/blob/master/Export-YouTube-subscriptions.md">
            <a>Import YouTube subscriptions:</a>
          </Link>
        </div>
        <label className="flex flex-col items-center px-4 py-6 text-blue rounded-lg shadow-lg tracking-wide uppercase cursor-pointer">
          {!isFilePickedYT ? (
            <svg
              className="w-8 h-8"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
            >
              <path d="M16.88 9.1A4 4 0 0 1 16 17H5a5 5 0 0 1-1-9.9V7a3 3 0 0 1 4.52-2.59A4.98 4.98 0 0 1 17 8c0 .38-.04.74-.12 1.1zM11 11h3l-4-4-4 4h3v3h2v-3z" />
            </svg>
          ) : (
            <p>{selectedFileYT.name}</p>
          )}
          <input
            type="file"
            className="hidden"
            onChange={changeHandlerYouTube}
          />
        </label>
        <button
          className="bg-red-500 px-4 py-2 mt-4 text-xs font-semibold tracking-wider text-white rounded hover:bg-blue-600"
          onClick={handleSubmissionYouTube}
        >
          Import
        </button>
      </BoxForContent>

      <BoxForContent>
        <div>
          <Link href="">
            <a>Import BitChute subscriptions:</a>
          </Link>
        </div>
        <label className="flex flex-col items-center px-4 py-6 text-blue rounded-lg shadow-lg tracking-wide uppercase cursor-pointer">
          {!isFilePickedBT ? (
            <svg
              className="w-8 h-8"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
            >
              <path d="M16.88 9.1A4 4 0 0 1 16 17H5a5 5 0 0 1-1-9.9V7a3 3 0 0 1 4.52-2.59A4.98 4.98 0 0 1 17 8c0 .38-.04.74-.12 1.1zM11 11h3l-4-4-4 4h3v3h2v-3z" />
            </svg>
          ) : (
            <p>{selectedFileBT.name}</p>
          )}
          <input type="file" className="hidden" onChange={changeHandlerBT} />
        </label>
        <button
          className="bg-green-500 px-4 py-2 mt-4 text-xs font-semibold tracking-wider text-white rounded hover:bg-blue-600"
          onClick={handleSubmissionBT}
        >
          Import
        </button>
      </BoxForContent>

      <BoxForContent>
        <label>ReTube subscriptions</label>
        <div className="grid justify-center">
          <a
            type="button"
            className="bg-red-500 px-4 py-2 mt-4 ml-2 text-xs font-semibold tracking-wider text-white rounded hover:bg-blue-600"
            href={`data:text/json;charset=utf-8,${encodeURIComponent(
              JSON.stringify(subsReadOnly)
            )}`}
            download="subscriptions.json"
          >
            Export
          </a>

          <BoxForContent>
            <div>
              <Link href="">
                <a>Import ReTube subscriptions:</a>
              </Link>
            </div>
            <label className="flex flex-col items-center px-4 py-6 text-blue rounded-lg shadow-lg tracking-wide uppercase cursor-pointer">
              {!isFilePickedRT ? (
                <svg
                  className="w-8 h-8"
                  fill="currentColor"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                >
                  <path d="M16.88 9.1A4 4 0 0 1 16 17H5a5 5 0 0 1-1-9.9V7a3 3 0 0 1 4.52-2.59A4.98 4.98 0 0 1 17 8c0 .38-.04.74-.12 1.1zM11 11h3l-4-4-4 4h3v3h2v-3z" />
                </svg>
              ) : (
                <p>{selectedFileRT.name}</p>
              )}
              <input
                type="file"
                className="hidden"
                onChange={changeHandlerRT}
              />
            </label>
            <button
              className="bg-blue-500 px-4 py-2 mt-4 text-xs font-semibold tracking-wider text-white rounded hover:bg-blue-600 hover:scale-110 motion-reduce:transform-none"
              onClick={handleSubmissionRT}
            >
              Import
            </button>
          </BoxForContent>
        </div>
      </BoxForContent>
    </div>
  );
};

export default Settings;
