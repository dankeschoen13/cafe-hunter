module.exports = {
  plugins: [
    require('postcss-nested'), // 1. Run the Sass-style string gluer first
    require('postcss-preset-env')({
      stage: 1,
      features: {
        'nesting-rules': false // 2. Tell the W3C purist module to completely shut off
      }
    })
  ]
}