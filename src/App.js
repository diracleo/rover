import React, {useEffect, useRef, useState} from 'react';
import { isResponseOk } from './utils.js';
import logo from './logo.svg';
import './App.css';
import nipplejs from 'nipplejs';
//import 'bootstrap/dist/css/bootstrap.min.css';
import '@forevolve/bootstrap-dark/dist/css/bootstrap-dark.min.css'
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

const maxForce = 2.5;
const maxInput = 255;
const inputPrecision = 51;
  
function App() {
  const left = useRef(null);
  const right = useRef(null);
  const leftData = useRef(0);
  const rightData = useRef(0);
  const leftDir = useRef(1);
  const rightDir = useRef(1);
  const prevLeftData = useRef(0);
  const prevRightData = useRef(0);
  const commandTimer = useRef(null);
  const managerLeft = useRef(null);
  const managerRight = useRef(null);
  
  const [ai, setAi] = useState(false);
  
  function convertToInput(value, dir) {
    value = Math.round(value / maxForce * maxInput);
    if (value > maxInput) {
	  value = maxInput;
	}
	value *= dir;
	value = Math.ceil(value / inputPrecision) * inputPrecision;
	return value;
  }
  
  useEffect(() => {
    const optionsLeft = {
      zone: left.current,
      lockY: true,
      shape: "square",
    };
    managerLeft.current = nipplejs.create(optionsLeft);
    const optionsRight = {
      zone: right.current,
      lockY: true,
      shape: "square",
    };
    managerRight.current = nipplejs.create(optionsRight);
    
    managerLeft.current.on('start end', (evt, data) => {
      leftData.current = 0;
      setAi(false);
    }).on('move', (evt, data) => {
	  leftData.current = convertToInput(data.force, leftDir.current);
    }).on('dir:up', (evt, data) => {
      leftDir.current = 1;
    }).on('dir:down', (evt, data) => {
      leftDir.current = -1;
    });
    
    managerRight.current.on('start end', (evt, data) => {
      rightData.current = 0;
      setAi(false);
    }).on('move', (evt, data) => {
      rightData.current = convertToInput(data.force, rightDir.current);
    }).on('dir:up', (evt, data) => {
      rightDir.current = 1;
    }).on('dir:down', (evt, data) => {
      rightDir.current = -1;
    });
    
    commandTimer.current = setInterval(() => {
      if (!ai && (leftData.current !== prevLeftData.current || rightData.current !== prevRightData.current)) {
        let q = '';
		q += 'left='+leftData.current;
		q += '&right='+rightData.current;
        fetch('command/?'+q)
        .then(isResponseOk)
        .then((data) => {
          prevLeftData.current = parseInt(data.left);
          prevRightData.current = parseInt(data.right);
        })
        .catch((error) => {
		  //console.log(error.message);
	    });
      }
    }, 200);
    
  }, []);
  
  useEffect(() => {
    let q = 'enabled=' + (ai ? '1' : '0');
    q += '&type=motion';
	fetch('ai/?'+q)
	.then(isResponseOk)
	.then((data) => {
	  
	})
	.catch((error) => {
      console.log(error.message);
	});
  }, [ai]);
  
  return (
    <div className="App">
      <div id="menu">
	    <Form.Check type="switch" id="ai-switch" label="AI" checked={ai} onChange={(evt) => setAi(evt.target.checked)} />
      </div>
	  <div id="controls">
        <div id="left" ref={left}></div>
        <div id="right" ref={right}></div>
      </div>
    </div>
  );
}

export default App;
