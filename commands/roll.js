const { SlashCommandBuilder, ClientUser, Message, EmbedBuilder } = require("discord.js");

module.exports = {
  data: new SlashCommandBuilder()
  .setName("roll")
  .setDescription("Rola um dado com valor escolhido")
  .addIntegerOption(option =>
    option.setName('d')
    .setDescription('Valor do dado')
    .setRequired(true)
    .setMinValue(2)
  ),

  async execute(interaction) {
    const userDice = interaction.options.getInteger('d');
    const diceroll = Math.floor(Math.random() * userDice) + 1;

    if (userDice == 20 && diceroll == 20) {
      const embed = new EmbedBuilder()
        .setColor("Green")
        .setAuthor({ name: "D" + userDice + " 🎲" })
        .addFields(
          { name: "**ACERTO CRÍTICO!**", value: " " },
          { name: " ", value: "**<@" + interaction.member.id + ">** rolou um " + "**" + diceroll + "**" }
        )
        .setImage("https://i.ibb.co/wyQPZcT/success.gif");

      interaction.reply({ embeds: [ embed ] });

    } else if (userDice == 20 && diceroll == 1) {
      const embed = new EmbedBuilder()
      .setColor("Red")
      .setAuthor({ name: "D" + userDice + " 🎲"})
      .addFields(
        { name: "**FALHA CRÍTICA!**", value: " " },
        { name: " ", value: "**<@" + interaction.member.id + ">** rolou um " + "**" + diceroll + "**" }
      )
      .setImage("https://i.ibb.co/N9wwKW8/fail.gif");

      interaction.reply({ embeds: [ embed ] });

    } else {
      const embed = new EmbedBuilder()
      .setColor("Blue")
      .setAuthor({ name: "D" + userDice + " 🎲"})
      .addFields(
        { name: " ", value: "**<@" + interaction.member.id + ">** rolou um " + "**" + diceroll + "**" }
      );

      interaction.reply({ embeds: [ embed ] });
    }
  },
};