#!/usr/bin/env bash

USAGE=" # USAGE: client_manager.sh [vtr1/vtr2/vtr3/vta1 / vtr/vta/vfs] [check/run] [reformation/contacted/risk]"
APP="${1}"
OP="${2}"

if [ "${APP}" == "vtr1" ]; then
  IP="10.122.64.230"
  PORT="50211"
elif [ "${APP}" == "vtr2" ]; then
  IP="10.122.64.230"
  PORT="50212"
elif [ "${APP}" == "vtr3" ]; then
  IP="10.122.64.118"
  PORT="50213"
elif [ "${APP}" == "vta1" ]; then
  IP="10.122.64.118"
  PORT="50311"
  OP_MODE="${3}"
elif [ "${APP}" == "vta1" ]; then
  IP="10.122.64.118"
  PORT="50311"
  OP_MODE="${3}"
elif [ "${APP}" == "vfs" ]; then
  IP="10.122.64.118"
  PORT="50331"
else
  echo ""
  echo "${USAGE}"
  echo ""
fi

if [ "${OP}" == "check" ]; then
  # shellcheck disable=SC2016
  CMD='curl -X POST -H "Content-Type: application/json"  http://${IP}:${PORT}/check'
  # CMD="curl -X POST -H "Content-Type: application/json"  http://127.0.0.1:${PORT}/check"
  echo ""
  echo "${CMD}"
  eval "${CMD}"
  echo ""
elif [ "${OP}" == "run" ]; then

  if [ "${APP}" == "vtr1" ]; then

    rm -rf Client/1
    mkdir Client/1
    mkdir Client/1/Details

    curl -X POST http://"${IP}":"${PORT}"/run \
      -H "Content-Type: application/json" \
      -d '{"method": "temporal",
          " src_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Input/tracking_1_10s.mp4",
            "privacy_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/1/rst.tracking_1_10s.mp4",
            "vid_json_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/1/rst.tracking_1_10s.json",
            "fps": "1",
            "details_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/1/Details"}'

  elif [ "${APP}" == "vtr2" ]; then

    rm -rf Client/2
    mkdir Client/2
    mkdir Client/2/Details

    curl -X POST http://"${IP}":"${PORT}"/run \
      -H "Content-Type: application/json" \
      -d '{"src_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Input/tracking_1_10s.mp4",
            "privacy_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/2/rst.tracking_1_10s.mp4",
            "vid_json_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/2/rst.tracking_1_10s.json",
            "fps": "1",
            "details_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/2/Details"}'

  elif [ "${APP}" == "vtr3" ]; then

    CORENAME="20211119_cc1"
    rm -rf Client/"${CORENAME}"
    mkdir Client/"${CORENAME}"
    mkdir Client/"${CORENAME}"

    curl -X POST http://"${IP}":"${PORT}"/run \
     -H "Content-Type: application/json" \
     -d '{"src_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Input/20211119_cc1.mp4",
          "privacy_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/20211119_cc1/privacy.20211119_cc1.mp4",
          "vid_json_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/20211119_cc1/20211119_cc1.vtr.json",
          "fps": "10",
          "details_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/20211119_cc1/Details"}'
    #  -H "Content-Type: application/json" \
    #  -d '{"src_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Input/S#_5_6_7_8.mp4",
    #       "privacy_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/S#_5_6_7_8/privacy.S#_5_6_7_8.mp4",
    #       "vid_json_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/S#_5_6_7_8/S#_5_6_7_8.vtr.json",
    #       "fps": "10",
    #       "details_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/S#_5_6_7_8/Details"}'
    #  -d '{"src_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Input/tracking_1_10s.mp4",
    #         "privacy_vid_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/3/privacy.tracking_1_10s.mp4",
    #         "vid_json_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/3/rst.tracking_1_10s.json",
    #         "fps": "1",
    #         "details_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Client/3/Details"}'

  elif [ "${APP}" == "vta1" ]; then

    if [ "${OP_MODE}" == "reformation" ]; then
      rm -rf Client/vta1
      mkdir Client/vta1

      curl -X POST http://"${IP}":"${PORT}"/run \
        -H "Content-Type: application/json" \
        -d '{"op_mode":"reformation",
            "in_vid_content_meta_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Output.vtr/S#_5_6_7_8.vtr.json",
            "in_vid_tracking_meta_url":"",
            "out_vid_tracking_meta_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Client/vta1/S#_5_6_7_8.vta1.json",
            "src_vid_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Input/S#_5_6_7_8.mp4",
            "rst_vid_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Client/vta1/S#_5_6_7_8.vta1.mp4",
            "trackid_update_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Output.vtr/S#_5_6_7_8.trackid.csv"}'

    elif [ "${OP_MODE}" == "contacted" ]; then

      curl -X POST http://"${IP}":"${PORT}"/run \
        -H "Content-Type: application/json" \
        -d '{"op_mode":"contacted",
            "in_vid_content_meta_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Output.vtr/S#_5_6_7_8.vtr.json",
            "in_vid_tracking_meta_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Client/vta1/S#_5_6_7_8.vta1.infected.json",
            "out_vid_tracking_meta_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Client/vta1/S#_5_6_7_8.vta1.infected.vta2.json",
            "src_vid_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Input/S#_5_6_7_8.mp4",
            "rst_vid_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Client/vta1/S#_5_6_7_8.vta2.mp4",
            "trackid_update_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Output.vtr/S#_5_6_7_8.trackid.csv"}'

    elif [ "${OP_MODE}" == "risk" ]; then

      curl -X POST http://"${IP}":"${PORT}"/run \
        -H "Content-Type: application/json" \
        -d '{"op_mode":"risk",
            "in_vid_content_meta_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Output.vtr/S#_5_6_7_8.vtr.json",
            "in_vid_tracking_meta_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Client/vta1/S#_5_6_7_8.vta1.infected.vta2.contacted.json",
            "out_vid_tracking_meta_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Client/vta1/S#_5_6_7_8.vta1.infected.vta2.contacted.risk.json",
            "src_vid_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Input/S#_5_6_7_8.mp4",
            "rst_vid_url": "/home/hoon/Workspace/System/VidTrkAnalysis/Client/vta1/S#_5_6_7_8.vta3.mp4",
            "trackid_update_url":"/home/hoon/Workspace/System/VidTrkAnalysis/Output.vtr/S#_5_6_7_8.trackid.csv"}'

    else
      pass
    fi

  elif [ "${APP}" == "vfs" ]; then

    rm -rf Client
    mkdir Client
    mkdir Client/Details

    curl -X POST http://"${IP}":"${PORT}"/run \
      -H "Content-Type: application/json" \
      -d '{"vid_content_meta_url": "./Input/20211119_cc1/20211119_cc1.vcm.json",
           "src_vid_url":"./Input/20211119_cc1//20211119_cc1.mp4",
           "infected_picture_url":"./Input/20211119_cc1/infected_face1.png",
           "rst_vid_url":"./Client/20211119_cc1.vfs.mp4",
           "rst_img_folder_url":"./Client/Details",
           "N": "100"}'
    #   -d '{"vid_content_meta_url": "./Input/S#_5_6_7_8/S#_5_6_7_8.vcm.json",
    #        "src_vid_url":"./Input/S#_5_6_7_8/S#_5_6_7_8.mp4",
    #        "infected_picture_url":"./Input/S#_5_6_7_8/infected_face.png",
    #        "rst_vid_url":"./Client/S#_5_6_7_8.vfs.mp4",
    #        "rst_img_folder_url":"./Client/Details",
    #        "N": "100"}'
  else
    echo ""
    echo "${USAGE}"
    echo ""
  fi

else
  echo ""
  echo "${USAGE}"
  echo ""
fi
