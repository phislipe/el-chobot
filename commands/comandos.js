const { SlashCommandBuilder, EmbedBuilder } = require("discord.js");

module.exports = {
  data: new SlashCommandBuilder()
  .setName("comandos")
  .setDescription("Exibe lista de comandos do bot"),
  async execute(interaction) {

    const embed = new EmbedBuilder()
      .setColor("Yellow")
      // .setAuthor({ name: "El Chobot - Comandos" })
      .addFields(
        { name: "`/comandos`", value: "Exibe lista de comandos do bot" }, 
        { name: "`/convite`", value: "Envia um link com convite para o servidor" }, 
        { name: "`/roll`", value: "Rola um dado com valor escolhido" }
      );

    interaction.reply({ embeds: [embed] });
  },
};