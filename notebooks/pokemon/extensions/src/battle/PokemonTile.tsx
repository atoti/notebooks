import React, { useState } from "react";
import styles from './battle.module.css';

export const PokemonTile = ({ pokemon }) => {

  const [hover, setHover] = useState(false);

  const imgName = pokemon.toLowerCase().replace(/[^a-z0-9 ]/g, "").replace(/\s+/g, "-");

  return (
    <div 
      style={{height: '100%', width: '100%', wordWrap: 'break-word'}} 
      onMouseEnter={() => {setHover(true)}} 
      onMouseLeave={() => {setHover(false)}}
    >
      <img 
        className={hover ? styles.pokemontile : null} 
        style={{height:'auto', maxWidth: '100px', marginLeft: '10px', marginRight: '20px'}} 
        src={ require(`../resources/images/${imgName}.png`).default }
      />
      {pokemon}
    </div>
  );
};
