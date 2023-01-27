const { SlashCommandBuilder, EmbedBuilder } = require("discord.js");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("convite")
    .setDescription("Envia um link com convite para o servidor"),
  async execute(interaction) {
    const embed = new EmbedBuilder()
    .setColor([47, 49, 54])
    .setImage("https://i.ibb.co/fn7VvQZ/welcome.gif");

    interaction.reply({ embeds: [embed], content: "https://discord.gg/D48QWY6MhK" });
  },
};