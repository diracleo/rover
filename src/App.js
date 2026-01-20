import React, {useEffect, useRef} from 'react';
import { isResponseOk } from './utils.js';
import './App.css';
import nipplejs from 'nipplejs';
import '@forevolve/bootstrap-dark/dist/css/bootstrap-dark.min.css';

const convertNippleData = (data) => {
  let modifier = 1;
  if (data.direction.x === 'left' || data.direction.y === 'down') {
    modifier = -1;
  }
  return Math.round(data.force * modifier * 100);
};

function App() {
  const drive = useRef(null);
  const steer = useRef(null);
  const managerDrive = useRef(null);
  const managerSteer = useRef(null);
  const driveValue = useRef(0);
  const steerValue = useRef(0);
  const driveValuePrev = useRef(0);
  const steerValuePrev = useRef(0);
  const commandTimer = useRef(null);
  
  useEffect(() => {
    const optionsDrive = {
      zone: drive.current,
      lockY: true,
      shape: "square",
    };
    managerDrive.current = nipplejs.create(optionsDrive);
    const optionsSteer = {
      zone: steer.current,
      lockX: true,
      shape: "square",
    };
    managerSteer.current = nipplejs.create(optionsSteer);

    managerDrive.current.on('start end', (evt, data) => {
      driveValue.current = 0;
    }).on('move', (evt, data) => {
      if (data.force && data.direction) {
	      driveValue.current = convertNippleData(data);
      }
    });

    managerSteer.current.on('start end', (evt, data) => {
      steerValue.current = 0;
    }).on('move', (evt, data) => {
      if (data.force && data.direction) {
	      steerValue.current = convertNippleData(data);
      }
    });

    commandTimer.current = setInterval(() => {
      if (driveValue.current !== driveValuePrev.current || steerValue.current !== steerValuePrev.current) {
        let q = '';
		    q += 'drive='+driveValue.current;
		    q += '&steer='+steerValue.current;
        fetch('command/?'+q)
        .then(isResponseOk)
        .then((data) => {
          driveValuePrev.current = parseInt(data.drive);
          steerValuePrev.current = parseInt(data.steer);
        })
        .catch((error) => {
		      //console.log(error.message);
	      });
      }
    }, 200);
  }, []);

  return (
    <div className="App">
	    <div id="controls">
        <div id="drive" ref={drive}></div>
        <div id="steer" ref={steer}></div>
      </div>
    </div>
  );
}

export default App;
